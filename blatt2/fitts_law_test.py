#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import itertools
import random
from PyQt4 import QtGui, QtCore


class Test(QtGui.QWidget):

    def __init__(self, file):
        super(Test, self).__init__()
        self.counter = 0
        self.readTestFile(file)
        self.initUI()
        self.initTest()

    def initUI(self):
        self.text = "Click on Red Circles"
        self.setGeometry(10, 10, 1024, 768)
        #self.showMaximized()
        self.setWindowTitle("Fitts's Law Test")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        #self.button = QtGui.QPushButton("Click here", self)
        #self.button.move(50, self.height()/2)
        #self.button.clicked.connect(self.buttonClick)
        self.show()
        self.center = QtCore.QPoint(self.width() / 2, self.height() / 2)

    def initTest(self):
        #self.repaint()
        self.combs = 4 * list(itertools.product(self.dists, self.widths))
        random.shuffle(self.combs)
        self.startTest()

    def buttonClick(self):
        print "Button clicked!"

    def readTestFile(self, file):
        fobj = open(file, "r")
        for line in fobj:
            line = line.strip()
            vals = line.split(":")
            if(vals[0] == "USER"):
                self.id = int(vals[1])
            elif(vals[0] == "WIDTHS"):
                self.widths = vals[1].split(",")
            elif(vals[0] == "DISTANCES"):
                self.dists = vals[1].split(",")
        fobj.close()

    def startTest(self):
        self.start = True
        testvals = self.combs[0]
        tx = self.center.x() + int(int(testvals[0])/2)
        sx = self.center.x() - int(int(testvals[0])/2)
        y = self.center.y()
        self.target = QtCore.QPoint(tx, y)
        self.start = QtCore.QPoint(sx, y)
        self.radius = int(int(testvals[1])/2)

    def nextTest(self):
        self.counter += 1
        if(self.counter < len(self.combs)):
            testvals = self.combs[self.counter]
            if(self.counter % 2) == 0:
                #target right
                tx = self.center.x() + int(int(testvals[0])/2)
                sx = self.center.x() - int(int(testvals[0])/2)
            else:
                #target left
                tx = self.center.x() - int(int(testvals[0])/2)
                sx = self.center.x() + int(int(testvals[0])/2)
            y = self.center.y()
            self.target = QtCore.QPoint(tx, y)
            self.start = QtCore.QPoint(sx, y)
            self.radius = int(int(testvals[1])/2)
        self.repaint()

    def mousePressEvent(self, event):
        p = event.pos()
        #print p
        x1 = self.target.x() - self.radius
        x2 = self.target.x() + self.radius
        y1 = self.target.y() - self.radius
        y2 = self.target.y() + self.radius
        if((p.x() >= x1 and p.x() <= x2) and (p.y() >= y1 and p.y() <= y2)):
            print "in Circle"
            self.nextTest()

    def mouseMoveEvent(self, event):
        print event.pos()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        #self.drawCircle(event, qp, 10, 20, 50)
        self.drawStart(event, qp)
        self.drawTarget(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 32))
        text = "Click on red circle: "+str(self.counter)
        qp.drawText(event.rect(), QtCore.Qt.AlignHCenter, text)

    def drawStart(self, event, qp):
        qp.setBrush(QtGui.QColor(34, 34, 200))
        qp.drawEllipse(self.start, self.radius, self.radius)

    def drawTarget(self, event, qp):
        qp.setBrush(QtGui.QColor(200, 34, 34))
        qp.drawEllipse(self.target, self.radius, self.radius)

    def drawCircle(self, event, qp, posX, posY, radius):
        qp.setBrush(QtGui.QColor(34, 34, 200))
        qp.drawEllipse(posX, posY, radius, radius)
        self.posX = posX
        self.posY = posY
        self.radius = radius


def main():
    #file = raw_input("Testfile: ")
    file = "test.txt"
    app = QtGui.QApplication(sys.argv)
    test = Test(file)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
