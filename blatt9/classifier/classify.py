#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
import pyqtgraph as pg

import wiimote_node
import filereadernode
import classifier


class CategoryVisualizerNode(Node):

    nodeName = "VisNode"

    def __init__(self, name):
        terminals = {
            'dataIn': dict(io='in'),
        }
        self.label = None
        Node.__init__(self, name, terminals=terminals)

    def setLabel(self, label):
        self.label = label

    def process(self, **kwds):
        #print kwds['dataIn']
        if self.label is not None:
            self.label.setText(kwds['dataIn'])

fclib.registerNodeType(CategoryVisualizerNode, [('Data',)])


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.setWindowTitle('WiimoteNode demo')
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
    label = QtGui.QLabel("You're not moving")

    layout.addWidget(label, 0, 1)
    layout.addWidget(pw1, 0, 2)
    pw1.setYRange(0, 1024)

    pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
    pw1Node.setPlot(pw1)

    wiimoteNode = fc.createNode('Wiimote', pos=(0, 0), )
    if len(sys.argv) > 1:
        wiimoteNode.setBTAddress(sys.argv[1])
    else:
        wiimoteNode.setBTAddress("b8:ae:6e:1b:ad:a0")

    bufferNode = fc.createNode('Buffer', pos=(150, 0))

    fileNode = fc.createNode('FileReader', pos=(0, 0), )

    fftNodeWii = fc.createNode('FFTNode', pos=(0, 0), )
    fftNodeFile = fc.createNode('FFTNode', pos=(0, 0), )
    svmNode = fc.createNode('SVMNode', pos=(0, 0), )

    visNode = fc.createNode('VisNode', pos=(0, 0), )
    visNode.setLabel(label)

    fc.connectTerminals(wiimoteNode['accelX'], bufferNode['dataInX'])
    fc.connectTerminals(wiimoteNode['accelY'], bufferNode['dataInY'])
    fc.connectTerminals(wiimoteNode['accelZ'], bufferNode['dataInZ'])
    fc.connectTerminals(bufferNode['dataOut'], fftNodeWii['dataIn'])
    fc.connectTerminals(bufferNode['dataOut'], pw1Node['In'])

    fc.connectTerminals(fileNode['fileVals'], fftNodeFile['dataIn'])
    fc.connectTerminals(fileNode['category'], svmNode['categories'])
    fc.connectTerminals(fftNodeFile['dataOut'], svmNode['trainigData'])
    fc.connectTerminals(fftNodeWii['dataOut'], svmNode['classifyData'])

    fc.connectTerminals(svmNode['classification'], visNode['dataIn'])

    win.show()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()