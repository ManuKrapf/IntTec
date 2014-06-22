#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

from pyqtgraph.flowchart import Flowchart, Node
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from scipy import fft, arange

import wiimote
import wiimote_node


class ActivityNode(CtrlNode):
    """
    Buffers the last n samples provided on input and provides them as a list of
    length n on output.
    A spinbox widget allows for setting the size of the buffer.
    Default size is 32 samples.
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
        #print "init Activity Node"
        self._buffer = np.array([])
        self.count = 0
        self.coords = []
        self.filter = []
        self.a1 = {
            'x': 605,
            'y': 512,
            'z': 550,
            'offset': 50
            }
        self.a2 = {
            'x': 0,
            'y': 0,
            'z': 0,
            'offset': 50
            }
        self.a3 = {
            'x': 0,
            'y': 0,
            'z': 0,
            'offset': 50
            }
        CtrlNode.__init__(self, name, terminals=terminals)

    def getSquareSignal(self, y):
        kernel = [0 for i in range(0, len(y))]
        for i in range(1, len(kernel)/2):
            kernel[(i*2)-1] = 1
        sqsig = np.convolve(y, kernel, mode='same')
        return sqsig

    def getFFT(self, y, Fs):
        #print y
        #Fs = 150.0;  # sampling rate
        #Ts = 1.0/Fs  # sampling interval
        #t = arange(0, 1, Ts)  # time vector

        #ff = 5.5  # frequency of the signal
        #y = np.sin(2*np.pi*ff*t)

        #y = self.getSquareSignal(y)
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
        val = self.coords[0]
        #sma =

        #if(val in range(0, 600)):
        #    label.setText("You're not moving")

        if(val in range(600, 620)):
            label.setText("You're walking")

        elif(val in range(621, 750)):
            label.setText("You're running")

        elif(val in range(751, 1000)):
            label.setText("You're cycling")

    def printVals(self):
        self.count += 1
        x, y, z = self.coords
        if(self.count == 100):
            print "X: "+str(x)+", Y: "+str(y)+", Z: "+str(z)
            fstr = ""
            for i in range(0, len(self.filter)-1):
                fstr += str(self.filter[i])+", "
            print fstr
            print "---------------------------------------"
            #print self.filter
            self.count = 0

    def process(self, **kwds):
        size = int(self.ctrls['size'].value())
        self.coords = [kwds['dataInX'],
                       kwds['dataInY'],
                       kwds['dataInZ']
                       ]
        self._buffer = np.append(self._buffer, kwds['dataInY'])
        self._buffer = self._buffer[-size:]
        self.filter = self.getFFT(self._buffer, 20.0)
        self.printVals()
        self.getActivity()
        output = self._buffer
        return {'dataOut': output}

fclib.registerNodeType(ActivityNode, [('Data',)])


if __name__ == '__main__':
    import sys
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
    bufferNode1 = fc.createNode('Buffer', pos=(150, 0))
    bufferNode2 = fc.createNode('Buffer', pos=(150, 0))
    bufferNode3 = fc.createNode('Buffer', pos=(150, 0))
    activityNode = fc.createNode('Activity', pos=(150, 0))

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