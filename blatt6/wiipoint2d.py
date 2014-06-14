#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
import wiimote
from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

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
            'irX': dict(io='out'),
            'irY': dict(io='out'),
        }
        self.wiimote = None
        self._acc_vals = []
        self._ir_vals = []
        self.no_avg = 10
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
        self.btaddr = "b8:ae:6e:1b:ad:a0"  # "b8:ae:6e:18:5d:ab"  # for ease of use
        self.text.setText(self.btaddr)
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_all_sensors)

        Node.__init__(self, name, terminals=terminals)

    def setBtAddr(self, btaddr):
        self.btaddr = btaddr

    def setWiiMote(self, wiimote):
        self.wiimote = wiimote

    def update_all_sensors(self):
        if self.wiimote == None:
            return
        self._acc_vals = self.wiimote.accelerometer
        self.getIrVal(self.wiimote.ir)
        #print self._ir_vals
        self.update()

    def update_accel(self, acc_vals):
        self._acc_vals = acc_vals
        self.update()

    def update_ir(self, ir_vals):
        self._ir_vals = ir_vals
        self.update()

    def getIrVal(self, curr_ir):
        biggest = [0, 0, -1]
        for ir_obj in curr_ir:
            if(biggest[2] < ir_obj["size"]):
                biggest = [ir_obj["x"], ir_obj["y"], ir_obj["size"]]
        if(len(self._ir_vals) >= self.no_avg):
            del self._ir_vals[0]
        self._ir_vals.append(biggest)

    def getAverage(self):
        sumX = 0
        sumY = 0
        for val in self._ir_vals:
            sumX += val[0]
            sumY += val[1]
        return [(sumX/len(self._ir_vals)), (sumY/len(self._ir_vals))]

    def ctrlWidget(self):
        return self.ui

    def connect_wiimote(self):
        self.btaddr = str(self.text.text()).strip()
        if self.wiimote is not None:
            self.wiimote.buttons.unregister_callback(self.button_click)
            self.wiimote.disconnect()
            self.wiimote = None
            self.connect_button.setText("connect")
            return
        if len(self.btaddr) == 17:
            self.connect_button.setText("connecting...")
            self.wiimote = wiimote.connect(self.btaddr)
            if self.wiimote == None:
                self.connect_button.setText("try again")
            else:
                self.connect_button.setText("disconnect")
                self.set_update_rate(self.update_rate_input.value())
                self.wiimote.buttons.register_callback(self.button_click)

    def button_click(self, button):
        if(self.wiimote.buttons["Plus"]):
            print(button)
        elif(self.wiimote.buttons["Minus"]):
            print(button)

    def set_update_rate(self, rate):
        if rate == 0:  # use callbacks for max. update rate
            self.wiimote.accelerometer.register_callback(self.update_accel)
            self.wiimote.ir.register_callback(self.update_ir)
            self.update_timer.stop()
        else:
            self.wiimote.accelerometer.unregister_callback(self.update_accel)
            self.wiimote.ir.unregister_callback(self.update_ir)
            self.update_timer.start(1000.0/rate)

    def process(self, **kwdargs):
        x, y, z = self._acc_vals
        ir_x, ir_y = self.getAverage()
        #print "X: "+str(ir_x)+", Y: "+str(ir_y)
        return {
            'accelX': np.array([x]),
            'accelY': np.array([y]),
            'accelZ': np.array([z]),
            'irX': np.array([ir_x]),
            'irY': np.array([ir_y]),
            }

fclib.registerNodeType(WiimoteNode, [('Sensor',)])


class Pointer2d(QtGui.QMainWindow):

    def __init__(self, btaddr):
        super(Pointer2d, self).__init__()
        self.btaddr = "b8:ae:6e:1b:ad:a0"
        self.wm = wiimote.connect(self.btaddr)
        self._ir_vals = []
        self.no_avg = 10
        self.t = QtCore.QTimer()
        self.t.timeout.connect(self.updateData)
        self.t.start(50)
        self.initPlot()

    def initPlot(self):
        #win = QtGui.QMainWindow()
        self.setWindowTitle('Pointer2D demo')
        self.cw = QtGui.QWidget()
        self.setCentralWidget(self.cw)
        layout = QtGui.QGridLayout()
        self.cw.setLayout(layout)

        ## Create an empty flowchart with a single input and output
        fc = Flowchart(terminals={
            'dataIn': {'io': 'in'},
            'dataOut': {'io': 'out'}
        })
        w = fc.widget()

        layout.addWidget(fc.widget(), 0, 0, 2, 1)

        pw1 = pg.PlotWidget()
        self.pw2 = pg.PlotWidget()
        layout.addWidget(pw1, 0, 1)
        layout.addWidget(self.pw2, 1, 1)
        pw1.setYRange(0, 1024)

        data = self.getIrData()
        self.pw2.plot([data[0]], [data[1]], pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w')

        pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
        pw1Node.setPlot(pw1)

        wiimoteNode = fc.createNode('Wiimote', pos=(0, 0), )
        wiimoteNode.setWiiMote(self.wm)
        bufferNode = fc.createNode('Buffer', pos=(150, 0))

        fc.connectTerminals(wiimoteNode['irX'], bufferNode['dataIn'])
        fc.connectTerminals(bufferNode['dataOut'], pw1Node['In'])

        self.show()
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def updateData(self):
        if(len(self._ir_vals) >= self.no_avg):
            del self._ir_vals[0]
        self._ir_vals.append(self.getIrData())
        avg = self.getAverage()
        self.pw2.plot([avg[0]], [avg[1]], pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w')
        self.update()

    def getIrData(self):
        ir_data = self.wm.ir
        biggest = [0, 0, -1]
        for ir_obj in ir_data:
            if(biggest[2] < ir_obj["size"]):
                biggest = [ir_obj["x"], ir_obj["y"], ir_obj["size"]]
        return biggest

    def getAverage(self):
        sumX = 0
        sumY = 0
        for val in self._ir_vals:
            sumX += val[0]
            sumY += val[1]
        return [(sumX/len(self._ir_vals)), (sumY/len(self._ir_vals))]


if __name__ == '__main__':
    app = QtGui.QApplication([])
    #pointer = Pointer2d("")
    win = QtGui.QMainWindow()
    win.setWindowTitle('Pointer2D demo')
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
    layout.addWidget(pw1, 0, 1)
    layout.addWidget(pw2, 1, 1)
    pw1.setYRange(0, 1024)

    #self.pw2.plot([data[0]], [data[1]], pen=(200,200,200), symbolBrush=(255,0,0), symbolPen='w')

    pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
    pw1Node.setPlot(pw1)

    wiimoteNode = fc.createNode('Wiimote', pos=(0, 0), )
    #wiimoteNode.setWiiMote(self.wm)
    bufferNode = fc.createNode('Buffer', pos=(150, 0))

    fc.connectTerminals(wiimoteNode['irX'], bufferNode['dataIn'])
    fc.connectTerminals(bufferNode['dataOut'], pw1Node['In'])

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
