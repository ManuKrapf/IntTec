#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

import wiimote
import wiimote_node as wnode
from pyqtgraph.flowchart import Flowchart, Node
import pyqtgraph.flowchart.library as fclib
from pyqtgraph import QtGui, QtCore
import pyqtgraph as pg


class Pointer2d(wnode.WiimoteNode):

    nodeName = "Pointer2d"

    def __init__(self, name):
        super(Pointer2d, self).__init__(name)
        self.ir_vals = []
        print self.btaddr

    def initUI(self):
        self.setWindowTitle("WiiMote 2D Pointer")
        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)
        self.layout = QtGui.QGridLayout()
        self.widget.setLayout(self.layout)

    def initChart(self):
        pass

fclib.registerNodeType(Pointer2d, [('Sensor',)])

if __name__ == '__main__':
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
        'dataOut': {'io': 'out'}
    })
    w = fc.widget()

    layout.addWidget(fc.widget(), 0, 0, 2, 1)

    pw1 = pg.PlotWidget()
    layout.addWidget(pw1, 0, 1)
    pw1.setYRange(0, 1024)

    pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
    pw1Node.setPlot(pw1)

    wiimoteNode = fc.createNode('Pointer2d', pos=(0, 0), )
    bufferNode = fc.createNode('Buffer', pos=(150, 0))

    fc.connectTerminals(wiimoteNode['accelX'], bufferNode['dataIn'])
    fc.connectTerminals(bufferNode['dataOut'], pw1Node['In'])

    win.show()
