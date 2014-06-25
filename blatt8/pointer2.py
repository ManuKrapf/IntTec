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


class GestureRecognition(object):

    def __init__(self):
        super(GestureRecognition, self).__init__()

    def resample(self, points, step=64):
        newPoints = []
        length = self.total_length(points)
        stepsize = length/step
        curpos = 0
        newPoints.append(points[0])
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
        return newPoints

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

    def rotateToZero(self, points):
        c = self.getCentroId(points)
        theta = math.atan2((c[1]-points[0][1]), (c[0]-points[0][0]))
        return self.rotateBy(points, theta)

    def rotateBy(self, points, theta):
        newPoints = []
        c = self.getCentroId(points)
        for p in points:
            qx = ((p[0]-c[0])*math.cos(theta))-(p[1]-c[1])*math.sin(theta+c[0])
            qy = ((p[0]-c[0])*math.sin(theta))-(p[1]-c[1])*math.cos(theta+c[0])
            newPoints.append([qx, qy])
        return newPoints

    def getCentroId(self, points):
        cId = [0, 0]
        for p in points:
            cId[0] += p[0]
            cId[1] += p[1]
        cId[0] /= len(points)
        cId[1] /= len(points)
        return cId

    def scaleToSquare(self, points, size):
        newPoints = []
        b = self.getBoundingBox(points)
        for p in points:
            qx = p[0]*(size/b[0])
            qy = p[1]*(size/b[0])
            newPoints.append([qx, qy])
        return newPoints

    def getBoundingBox(self, points):
        minX, minY = float("inf")
        maxX, maxY = float("-inf")
        for p in points:
            minX = min(p[0], minX)
            maxX = max(p[0], maxX)
            minY = min(p[1], minY)
            maxY = max(p[1], maxY)
        return [minX, minY, maxX-minX, maxY-minY]  # [minX, minY, width, height]

    def translateToOrigin(self, points):
        newPoints = []
        c = self.getCentroId(points)
        for p in points:
            qx = p[0]-c[0]
            qy = p[1]-c[1]
            newPoints.append([qx, qy])
        return newPoints

    def recognize(self, points, templates):
        b = float("inf")
        trec = None
        for t in templates:
            d = self.distanceAtBestAngle(points, t, 45, -45, 2)
            if(d < b):
                b = d
                trec = t
        score = 1-(b/0.5*math.sqrt(math.pow(size, 2)+math.pow(size, 2)))
        return score  # return template and score!!!

    def distanceAtBestAngle(self, points, temp, ta, tb, tdelta):
        phi = 0.5*(-1+math.sqrt(5))
        x1 = phi*ta + (1-phi)*tb
        f1 = self.distanceAtAngle(points, temp, x1)
        x2 = (1-phi)*ta + phi*tb
        f2 = self.distanceAtAngle(points, temp, x2)
        while(abs(tb-ta) > tdelta):
            if(f1 < f2):
                tb = x2
                x2 = x1
                f2 = f1
                x1 = phi*ta + (1-phi)*tb
                f1 = self.distanceAtAngle(points, temp, x1)
            else:
                ta = x1
                x1 = x2
                f1 = f2
                x2 = (1-phi)*ta + phi*tb
                f2 = self.distanceAtAngle(points, temp, x2)
        return min(f1, f2)

    def distanceAtAngle(self, points, temp, theta):
        newPoints = self.rotateBy(points, theta)
        d = self.pathDistance(newPoints, temp.points)
        return d

    def pathDistance(a, b):
        d = 0
        for i in range(0, len(a)):
            d += self.distance(a[i], b[i])
        return d/len(a)


class Pointer(QtGui.QDialog):

    def __init__(self, parent=None):
        super(Pointer, self).__init__(parent)
        self.btaddr = "b8:ae:6e:1b:ad:a0"
        #self.wm = wiimote.connect(self.btaddr)
        self.gr = GestureRecognition()
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

    def plotIt(self):
        np = self.gr.resample(self.ir_vals, self.step)
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