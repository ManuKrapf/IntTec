#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
import math
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
            'dataInX': dict(io='in'),
            'dataInY': dict(io='in'),
            'dataOutX': dict(io='out'),
            'dataOutY': dict(io='out'),
        }
        self._bufferX = np.array([])
        self._bufferY = np.array([])
        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, **kwds):
        size = int(self.ctrls['size'].value())
        self._bufferX = np.append(self._buffer, kwds['dataInX'])
        self._bufferX = self._buffer[-size:]
        self._bufferY = np.append(self._buffer, kwds['dataInY'])
        self._bufferY = self._buffer[-size:]
        outputX = self._bufferX
        outputY = self._bufferY
        return {'dataOutX': outputX, 'dataOutY': outputY}

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
            'irvals': dict(io='out'),
        }
        self.wiimote = None
        self._acc_vals = []
        self._ir_vals = []
        self._ir_vals_obj = {}
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
        self.connect_button.clicked.connect(
            self.connect_wiimote)
        self.btaddr = "b8:ae:6e:1b:ad:a0"
        self.text.setText(self.btaddr)
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_all_sensors)

        Node.__init__(self, name, terminals=terminals)

    def setBtAddr(self, btaddr):
        self.btaddr = btaddr
        self.connect_wiimote()
        return self.wiimote

    def update_all_sensors(self):
        if self.wiimote == None:
            return
        self._acc_vals = self.wiimote.accelerometer
        self._ir_vals_obj = self.wiimote.ir
        self.update()

    def update_accel(self, acc_vals):
        self._acc_vals = acc_vals
        self.update()

    def update_ir(self, ir_vals):
        self._ir_vals_obj = ir_vals
        self.update()

    def getIrVal(self):
        biggest = [0, 0, -1]
        for ir_obj in self._ir_vals_obj:
            if(biggest[2] < ir_obj["size"]):
                biggest = [ir_obj["x"], ir_obj["y"], ir_obj["size"]]
        if(len(self._ir_vals) >= self.no_avg):
            del self._ir_vals[0]
        #return biggest
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
                #self.wiimote.buttons.register_callback(self.button_click)

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
        self.getIrVal()
        ir_x, ir_y = self.getAverage()
        return {
            'accelX': np.array([x]),
            'accelY': np.array([y]),
            'accelZ': np.array([z]),
            'irX': np.array([ir_x]),
            'irY': np.array([ir_y]),
            'irvals': self._ir_vals_obj
            }

fclib.registerNodeType(WiimoteNode, [('Sensor',)])


class Pointer3d(pg.ScatterPlotItem):

    def __init__(self, btaddr):
        super(Pointer3d, self).__init__(pos=[(0, 0)])
        self.btaddr = btaddr
        self.wm = None
        self.ir_vals = []
        self.no_avg = 20
        self.initNode()
        self.t = QtCore.QTimer()
        self.t.timeout.connect(self.updateData)
        self.t.start(50)

    def initNode(self):
        self.ir_node = WiimoteNode("IrNode")
        self.wm = self.ir_node.setBtAddr(self.btaddr)
        self.wm.buttons.register_callback(self.button_click)
        #self.printData()

    def updateData(self):
        self.printData()

    def printData(self):
        self.ir_node.update_all_sensors()
        self.nodedata = self.ir_node.process()
        self.getBiggestVal(self.nodedata['irvals'])
        avg = self.getAverage()
        pos = [(avg[0], avg[1])]
        dist = self.getDistance()
        size = int(dist/10)
        #print size
        #self.clear()
        self.setData(pos=pos, size=size)

    def getBiggestVal(self, curr_ir):
        biggest1 = [0, 0, -1]
        biggest2 = [0, 0, -1]
        #print curr_ir
        for ir_obj in curr_ir:
            if(biggest1[2] < ir_obj["size"]):
                biggest2 = biggest1
                biggest1 = [ir_obj["x"], ir_obj["y"],
                            ir_obj["size"]]
            elif(biggest2[2] < ir_obj["size"]):
                biggest2 = [ir_obj["x"], ir_obj["y"],
                            ir_obj["size"]]
        if(len(self.ir_vals) >= self.no_avg):
            del self.ir_vals[0]
        temp = [(biggest1[0]+biggest2[0])/2,
                (biggest1[1]+biggest2[1])/2,
                (biggest1[2]+biggest2[2])/2]
        self.ir_vals.append(temp)

    def getAverage(self):
        sumX = 0
        sumY = 0
        sumSize = 0
        for val in self.ir_vals:
            sumX += val[0]
            sumY += val[1]
            sumSize += val[2]
        return [np.array([(sumX/len(self.ir_vals))]),
                np.array([(sumY/len(self.ir_vals))]),
                int(sumSize/len(self.ir_vals))]

    def getDistance(self):
        point = [self.ir_vals[len(self.ir_vals)-1][0],
                 self.ir_vals[len(self.ir_vals)-1][1]]
        wmote = [self.nodedata['accelX'],
                 self.nodedata['accelY']]
        dx_2 = math.pow(point[0] - wmote[0], 2)
        dy_2 = math.pow(point[1] - wmote[1], 2)
        dist = math.sqrt(dx_2 + dy_2)
        return dist

    def button_click(self, button):
        if(len(button) >= 1):
            if(button[0][1]) and (button[0][0] == "Plus"):
                if(self.no_avg < 40):
                    self.no_avg += 1
            elif(button[0][1]) and (button[0][0] == "Minus"):
                if(self.no_avg > 0):
                    self.no_avg -= 1

    def __del__(self):
        self.t.stop()
        self.wm.buttons.unregister_callback(self.button_click)


if __name__ == '__main__':
    btaddr = "b8:ae:6e:1b:ad:a0"
    if(len(sys.argv) > 1):
        btaddr = sys.argv[1]
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('Pointer2D demo')
    cw = QtGui.QWidget()
    win.setCentralWidget(cw)
    layout = QtGui.QGridLayout()
    cw.setLayout(layout)

    ## Create an empty flowchart with a single input and output
    fc = Flowchart(terminals={
        'dataIn': {'io': 'in'},
        'dataIn': {'io': 'in'},
        'dataOut': {'io': 'out'}
    })
    w = fc.widget()

    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    pw1 = pg.PlotWidget()
    pw2 = pg.PlotWidget()
    p3d = Pointer3d(btaddr)
    pw2.addItem(p3d)
    pw2.setYRange(0, 1024)
    pw2.setXRange(0, 1024)
    layout.addWidget(pw1, 0, 1)
    layout.addWidget(pw2, 1, 1)
    pw1.setYRange(0, 1024)

    pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
    pw1Node.setPlot(pw1)

    wiimoteNode = fc.createNode('Wiimote', pos=(0, 0), )
    bufferNode = fc.createNode('Buffer', pos=(150, 0))

    fc.connectTerminals(wiimoteNode['accelX'], bufferNode['dataInX'])
    fc.connectTerminals(bufferNode['dataOutX'], pw1Node['In'])

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
