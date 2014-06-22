#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from scipy import fft, arange

import wiimote


class BufferNode(CtrlNode):
    """
    Buffers the last n samples provided on input and provides them as a list of
    length n on output.
    A spinbox widget allows for setting the size of the buffer.
    Default size is 32 samples.
    """
    nodeName = "Buffer"
    uiTemplate = [
        ('size',  'spin', {'value': 32.0, 'step': 1.0, 'range': [0.0, 128.0]}),
    ]

    def __init__(self, name):
        terminals = {
            'dataIn': dict(io='in'),
            'dataOut': dict(io='out'),
        }
        self._buffer = np.array([])
        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        size = int(self.ctrls['size'].value())
        self._buffer = np.append(self._buffer, kwds['dataIn'])
        self._buffer = self._buffer[-size:]
        output = self._buffer
        return {'dataOut': output}

fclib.registerNodeType(BufferNode, [('Data',)])


class WiimoteNode(Node):
    """
    Outputs sensor data from a Wiimote.

    Supported sensors: accelerometer (3 axis)
    Text input box allows for setting a Bluetooth MAC address.
    Pressing the "connect" button tries connecting to the Wiimote.
    Update rate can be changed via a spinbox widget. Setting it to "0"
    activates callbacks everytime a new sensor value arrives (which is
    quite often -> performance hit)
    """
    nodeName = "Wiimote"

    def __init__(self, name):
        terminals = {
            'accelX': dict(io='out'),
            'accelY': dict(io='out'),
            'accelZ': dict(io='out'),
        }
        self.wiimote = None
        self._acc_vals = []
        self.ui = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()

        label = QtGui.QLabel("Bluetooth MAC address:")
        self.layout.addWidget(label)
        self.text = QtGui.QLineEdit()
        self.layout.addWidget(self.text)
        label2 = QtGui.QLabel("Update rate (Hz)")
        self.layout.addWidget(label2)
        self.update_rate_input = QtGui.QSpinBox()
        self.update_rate_input.setMinimum(0)
        self.update_rate_input.setMaximum(60)
        self.update_rate_input.setValue(20)
        self.update_rate_input.valueChanged.connect(self.set_update_rate)
        self.layout.addWidget(self.update_rate_input)

        self.connect_button = QtGui.QPushButton("connect")
        self.layout.addWidget(self.connect_button)
        self.ui.setLayout(self.layout)
        self.connect_button.clicked.connect(self.connect_wiimote)
        self.btaddr = "b8:ae:6e:1b:ad:a0"  # for ease of use
        self.text.setText(self.btaddr)
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_all_sensors)

        Node.__init__(self, name, terminals=terminals)

    def setBtAddr(self, btaddr):
        self.btaddr = btaddr
        self.connect_wiimote()

    def update_all_sensors(self):
        if self.wiimote is None:
            return
        self._acc_vals = self.wiimote.accelerometer
        # todo: other sensors...
        self.update()

    def update_accel(self, acc_vals):
        self._acc_vals = acc_vals
        self.update()

    def ctrlWidget(self):
        return self.ui

    def connect_wiimote(self):
        self.btaddr = str(self.text.text()).strip()
        if self.wiimote is not None:
            self.wiimote.disconnect()
            self.wiimote = None
            self.connect_button.setText("connect")
            return
        if len(self.btaddr) == 17:
            self.connect_button.setText("connecting...")
            self.wiimote = wiimote.connect(self.btaddr)
            if self.wiimote is None:
                self.connect_button.setText("try again")
            else:
                self.connect_button.setText("disconnect")
                self.set_update_rate(self.update_rate_input.value())

    def set_update_rate(self, rate):
        if rate == 0:  # use callbacks for max. update rate
            self.wiimote.accelerometer.register_callback(self.update_accel)
            self.update_timer.stop()
        else:
            self.wiimote.accelerometer.unregister_callback(self.update_accel)
            self.update_timer.start(1000.0/rate)

    def process(self, **kwdargs):
        x, y, z = self._acc_vals
        return {
            'accelX': np.array([x]),
            'accelY': np.array([y]),
            'accelZ': np.array([z])
            }

fclib.registerNodeType(WiimoteNode, [('Sensor',)])


class ActivityNode(CtrlNode):
    """
    This Node takes the values of the accelerometer and detects the activities
    standing, sitting, walking and running. The detection is based on the FFT
    and a square signal.
    """
    nodeName = "Activity"
    uiTemplate = [
        ('size',  'spin', {'value': 32.0, 'step': 1.0, 'range': [0.0, 128.0]}),
    ]

    def __init__(self, name):
        terminals = {
            'dataInX': dict(io='in'),
            'dataInY': dict(io='in'),
            'dataInZ': dict(io='in'),
            'dataOut': dict(io='out'),
        }
        self._buffer = np.array([])
        self.frq_buffer = np.array([])
        self.label = None
        self.count = 0
        self.coords = []
        self.filter = []
        CtrlNode.__init__(self, name, terminals=terminals)

    def setLabel(self, label):
        self.label = label  # sets the label to the node
        self.label.setText("Test123")

    def getSquareSignal(self, y):
        """
        Calcs a filter with a square signal and the values of the given
        parameter.
        """
        kernel = [0 for i in range(0, len(y))]
        for i in range(1, len(kernel)/2):
            kernel[(i*2)-1] = 1
        sqsig = np.convolve(y, kernel, mode='same')
        return sqsig

    def getFFT(self, y, Fs):
        """
        Calcs the FFT for the given values with a given Frequency
        """
        n = len(y)  # length of the signal
        k = arange(n)
        T = n/Fs
        frq = k/T  # two sides frequency range
        frq = frq[range(n/2)]  # one side frequency range

        Y = fft(y)/n  # fft computing and normalization
        Y = Y[range(n/2)]

        for i in range(0, len(Y)-1):
            Y[i] = abs(Y[i])

        return self.getSquareSignal(Y)

    def getActivity(self):
        """
        Decides with the calculated values which activitiy is done at the
        moment
        """
        frq = np.sum(self.frq_buffer)/len(self.frq_buffer)
        y = self.coords[1]

        if((frq >= 0.0) and (frq < 10.0)) and (y in range(550, 650)):
            self.label.setText("You're standing")
        elif((frq >= 0.0) and (frq < 10.0)) and (y in range(520, 550)):
            self.label.setText("You're sitting")
        elif((frq >= 10.0) and (frq < 40.0)) and (y in range(550, 650)):
            self.label.setText("You're walking")
        elif((frq >= 40.0) and (frq < 200.0)) and (y in range(550, 650)):
            self.label.setText("You're running")

    def process(self, **kwds):
        size = int(self.ctrls['size'].value())
        self.coords = [kwds['dataInX'][0],
                       kwds['dataInY'][0],
                       kwds['dataInZ'][0]
                       ]
        self._buffer = np.append(self._buffer, self.coords[1])
        self._buffer = self._buffer[-size:]
        self.filter = self.getFFT(self._buffer, 20.0)
        self.frq_buffer = np.append(self.frq_buffer, self.filter[1].real)
        self.frq_buffer = self.frq_buffer[-size:]
        self.getActivity()
        output = self._buffer
        return {'dataOut': output}

fclib.registerNodeType(ActivityNode, [('Data',)])


if __name__ == '__main__':
    btaddr = "b8:ae:6e:1b:ad:a0"
    if(len(sys.argv) > 1):
        btaddr = sys.argv[1]

    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('Activity Recognition')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    ## Create an empty flowchart with a single input and output
    fc = Flowchart(terminals={
        'dataIn': {'io': 'in'},
        'dataOut': {'io': 'out'}
    })
    w = fc.widget()

    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    pw1 = pg.PlotWidget()
    pw2 = pg.PlotWidget()
    pw3 = pg.PlotWidget()
    label = QtGui.QLabel("You're not moving")

    layout.addWidget(label, 0, 1)
    layout.addWidget(pw1, 1, 1)
    layout.addWidget(pw2, 2, 1)
    layout.addWidget(pw3, 3, 1)
    pw1.setYRange(0, 1024)
    pw2.setYRange(0, 1024)
    pw3.setYRange(0, 1024)

    pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
    pw1Node.setPlot(pw1)
    pw2Node = fc.createNode('PlotWidget', pos=(0, -150))
    pw2Node.setPlot(pw2)
    pw3Node = fc.createNode('PlotWidget', pos=(0, -150))
    pw3Node.setPlot(pw3)

    wiimoteNode = fc.createNode('Wiimote', pos=(0, 0), )
    wiimoteNode.setBtAddr(btaddr)
    bufferNode1 = fc.createNode('Buffer', pos=(150, 0))
    bufferNode2 = fc.createNode('Buffer', pos=(150, 0))
    bufferNode3 = fc.createNode('Buffer', pos=(150, 0))
    activityNode = fc.createNode('Activity', pos=(150, 0))
    activityNode.setLabel(label)

    fc.connectTerminals(wiimoteNode['accelX'], bufferNode1['dataIn'])
    fc.connectTerminals(wiimoteNode['accelY'], bufferNode2['dataIn'])
    fc.connectTerminals(wiimoteNode['accelZ'], bufferNode3['dataIn'])
    fc.connectTerminals(wiimoteNode['accelX'], activityNode['dataInX'])
    fc.connectTerminals(wiimoteNode['accelY'], activityNode['dataInY'])
    fc.connectTerminals(wiimoteNode['accelZ'], activityNode['dataInZ'])
    fc.connectTerminals(bufferNode1['dataOut'], pw1Node['In'])
    fc.connectTerminals(bufferNode2['dataOut'], pw2Node['In'])
    fc.connectTerminals(bufferNode3['dataOut'], pw3Node['In'])

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
