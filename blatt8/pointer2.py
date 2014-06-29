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

#from matplotlib import *


class Template(object):

    def __init__(self, name, points=[]):
        super(Template, self).__init__()
        self.name = name
        self.points = points

    def setPoints(self, points):
        self.points = points


class GestureRecognition(object):

    """
    Class for the recognition of gestures with the one
    dollar gesture recognizer.
    The class can recognize a gesture of a given set of
    points or store a new template with a set of points
    Sources for the architecture and functionality of the
    class:
    http://www.cs.columbia.edu/~coms6998-11/papers/
    dollargestures.pdf
    https://github.com/voidplus/onedollar-unistroke-
    recognizer/blob/master/src/de/voidplus/dollar/Recognizer.java
    """

    def __init__(self, size=100):
        super(GestureRecognition, self).__init__()
        self.templates = []
        self.size = size
        self.initTemplates()

    def initTemplates(self):
        # Square Template
        points = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0],
                  [5, 0], [6, 0], [7, 0], [8, 0], [9, 0],
                  [10, 0], [11, 0], [12, 0], [13, 0], [14, 0],
                  [15, 0], [15, 1], [15, 2], [15, 3], [15, 4],
                  [15, 5], [15, 6], [15, 7], [15, 8], [15, 9],
                  [15, 10], [15, 11], [15, 12], [15, 13], [15, 14],
                  [15, 15], [14, 15], [13, 15], [12, 15], [11, 15],
                  [10, 15], [9, 15], [8, 15], [7, 15], [6, 15],
                  [5, 15], [4, 15], [3, 15], [2, 15], [1, 15],
                  [0, 15], [0, 14], [0, 13], [0, 12], [0, 11],
                  [0, 10], [0, 9], [0, 8], [0, 7], [0, 6],
                  [0, 5], [0, 4], [0, 3], [0, 2], [0, 1],
                  ]
        newPoints = self.processRawData(points)
        temp = Template("Square", newPoints)
        self.templates.append(temp)
        # Circle Template
        points = []
        for i in range(64):
            a = i*5.625
            x = math.cos(a)
            y = math.sin(a)
            points.append([x, y])
        newPoints = self.processRawData(points)
        temp = Template("Circle", newPoints)
        self.templates.append(temp)
        # Triangle Template
        points = [[0, 0], [10, 0], [20, 0], [10, 10]]
        newPoints = self.processRawData(points)
        temp = Template("Triangle", newPoints)
        self.templates.append(temp)

    """
    Recognizing a template
    """
    def recognizeGesture(self, points):
        newPoints = self.processRawData(points)
        temp = self.recognize(newPoints, self.templates)
        return temp

    """
    Storing a new template
    """
    def storeTemplate(self, name, points):
        newPoints = self.processRawData(points)
        temp = Template(name, newPoints)
        self.templates.append(temp)

    """
    Processes the given raw data points to recognize a
    gesture or storing a new template
    """
    def processRawData(self, points):
        if(len(points) > 0):
            newPoints = self.resample(points)
            newPoints = self.rotateToZero(newPoints)
            newPoints = self.scaleToSquare(newPoints)
            newPoints = self.translateToOrigin(newPoints)
            return newPoints
        else:
            return 0

    """Step 1 from the 1 Dollar Gesture Recognizer"""
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
                newPoints.append([nx, ny])
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

    """Step 2 from the 1 Dollar Gesture Recognizer"""
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

    """Step 3 from the 1 Dollar Gesture Recognizer"""
    def scaleToSquare(self, points):
        newPoints = []
        b = self.getBoundingBox(points)
        for p in points:
            qx = p[0]*(self.size/b[2])
            qy = p[1]*(self.size/b[3])
            newPoints.append([qx, qy])
        return newPoints

    def getBoundingBox(self, points):
        minX = minY = float("inf")
        maxX = maxY = float("-inf")
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

    """Step 4 from the 1 Dollar Gesture Recognizer"""
    def recognize(self, points, templates):
        b = float("inf")
        trec = None
        for t in templates:
            d = self.distanceAtBestAngle(points, t, 45, -45, 2)
            if(d < b):
                b = d
                trec = t
        score = 1-(b/0.5*math.sqrt(math.pow(self.size, 2)+math.pow(self.size, 2)))
        return {'template': trec, 'score': score}

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

    def pathDistance(self, a, b):
        d = 0
        if(len(a) != len(b)):
            return float("inf")
        else:
            for i in range(0, len(a)):
                d += self.distance(a[i], b[i])
            return d/len(a)


class Pointer(QtGui.QDialog):

    def __init__(self, parent=None):
        super(Pointer, self).__init__(parent)
        self.btaddr = "E0:0C:7F:30:17:7D"  # "b8:ae:6e:1b:ad:a0"
        self.wm = wiimote.connect(self.btaddr)
        self.wm.buttons.register_callback(self.button_click)
        self.gr = GestureRecognition()
        #self.buffer = []
        self.curPos = []
        self.ir_vals = []
        self.recPoints = False
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
        # set the layout
        layout = QtGui.QVBoxLayout()
        self.status = QtGui.QLabel()
        self.status.setText("Press A for Recognition or B for Recording!")
        self.label = QtGui.QLabel()
        self.label.setText("No Gesture")
        layout.addWidget(self.toolbar)
        layout.addWidget(self.status)
        layout.addWidget(self.label)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def updateData(self):
        self.getIrData()
        self.plot()

    def plot(self):
        # create an axis
        ax = self.figure.add_subplot(111)
        # set axis limits
        ax.axis([0, 1000, 0, 1000])
        ax.autoscale(enable=False)
        # discards the old graph
        ax.hold(False)
        if(self.recPoints):
            data = self.ir_vals
            ax.plot(*zip(*data), ls="solid", marker='o', color='r')
        else:
            data = self.curPos
            ax.plot([data[0]], [data[1]], ls="solid", marker='o', color='r')
        # refresh canvas
        self.canvas.draw()

    def getIrData(self):
        irobj = self.wm.ir
        if(len(irobj) > 0):
            self.getBiggestVal(irobj)
        else:
            self.curPos = [0, 0]

    def getBiggestVal(self, curr_ir):
        biggest = [0, 0, -1]
        for ir_obj in curr_ir:
            if(biggest[2] < ir_obj["size"]):
                biggest = [ir_obj["x"], ir_obj["y"],
                           ir_obj['size']]
        if(len(self.ir_vals) >= self.step):
            del self.ir_vals[0]
        self.curPos = [biggest[0], biggest[1]]
        if(self.recPoints):
            self.ir_vals.append(self.curPos)
            self.ir_vals = self.ir_vals[-self.step:]

    def getAverage(self):
        sumX = 0
        sumY = 0
        if(len(self.ir_vals) > 0):
            for val in self.ir_vals:
                sumX += val[0]
                sumY += val[1]
            return [np.array([(sumX/len(self.ir_vals))]),
                    np.array([(sumY/len(self.ir_vals))]),
                    ]
        else:
            return [0, 0]

    def button_click(self, button):
        if(len(button) >= 1):
            if(button[0][0] == "A"):
                if(button[0][1]):
                    self.startRecognition()
                else:
                    self.stopRecognition()
            elif(button[0][0] == "B"):
                if(button[0][1]):
                    self.startRecording()
                else:
                    self.stopRecording()

    def startRecognition(self):
        self.status.setText("start Recognition")
        self.ir_vals = []
        self.recPoints = True

    def stopRecognition(self):
        self.status.setText("stop Recognition")
        self.recPoints = False
        temp = self.gr.recognizeGesture(self.ir_vals)
        self.label.setText(temp['template'].name)

    def startRecording(self):
        self.status.setText("start Recording")
        self.ir_vals = []
        self.recPoints = True

    def stopRecording(self):
        self.status.setText("stop Recording")
        self.recPoints = False

        # open dialog to allow custom template names via user input
        text, ok = QtGui.QtInputDialog.getText(self, "Save Template",
                                               "Template Name:")

        # if OK-button is pressed, save template name and points
        if (ok):
            self.gr.storeTemplate(str(text), self.ir_vals)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    pointer = Pointer()
    pointer.show()

    sys.exit(app.exec_())