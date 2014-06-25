#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
import wiimote
import math
import numpy as np
from pyqtgraph import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt

from matplotlib import *


class Pointer(QtGui.QDialog):

    def __init__(self, parent=None):
        super(Pointer, self).__init__(parent)
        self.btaddr = "b8:ae:6e:1b:ad:a0"
        #self.wm = wiimote.connect(self.btaddr)
        self.buffer = []
        self.ir_vals = []
        self.step = 64
        self.t = QtCore.QTimer()
        self.t.timeout.connect(self.updateData)
        self.t.start(50)
        self.initPlot()

    def initPlot(self):
        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        #self.button = QtGui.QPushButton('Plot')
        #self.button.clicked.connect(self.plot)

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        #layout.addWidget(self.button)
        self.setLayout(layout)

    def updateData(self):
        #self.getIrData()
        #avg = getAverage()
        self.ir_vals = [[0,1],[1,0],[2,-1],[3,0],[4,1],[5,0],[6,-1],[7,0],[8,1],[9,0],[10,-1],[11,0],[12,1],[13,0],[14,-1]]
        self.plotIt()

    def resample(self, points, step=64):
        newpoints = []
        length = self.total_length(points)
        stepsize = length/step
        curpos = 0
        newpoints.append(points[0])
        i = 1
        while i < len(points):
            p1 = points[i-1]
            d = self.distance(p1, points[i])
            if curpos+d >= stepsize:
                nx = p1[0] + ((stepsize-curpos)/d)*(points[i][0]-p1[0])
                ny = p1[1] + ((stepsize-curpos)/d)*(points[i][1]-p1[1])
                newpoints.append([nx, ny])
                points.insert(i, [nx, ny])
                curpos = 0
            else:
                curpos += d
            i += 1
        return newpoints

    def distance(self, p1, p2):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return math.sqrt(dx*dx+dy*dy)

    def total_length(self, points):
        p1 = points[0]
        length = 0.0
        for i in range(1, len(points)):
            length += self.distance(p1, points[i])
            p1 = points[i]
        return length

    def plotIt(self):
        np = self.resample(self.ir_vals, self.step)
        #ylim(-1.5, 1.5)
        #plot(*zip(*np), ls="solid", marker='o', color='r')
        self.plot(np)

    def plot(self, data):
        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.hold(False)

        # plot data
        ax.plot(*zip(*data), ls="solid", marker='o', color='r')

        # refresh canvas
        self.canvas.draw()

    def getIrData(self):
        irobj = self.wm.ir
        self.getBiggestVal(irobj)

    def getBiggestVal(self, curr_ir):
        biggest = [0, 0, -1]
        for ir_obj in curr_ir:
            if(biggest[2] < ir_obj["size"]):
                biggest = [ir_obj["x"], ir_obj["y"]]
        if(len(self.ir_vals) >= self.step):
            del self.ir_vals[0]
        self.ir_vals.append(biggest)

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


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    pointer = Pointer()
    pointer.show()

    sys.exit(app.exec_())