#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore


class Test(QtGui.QWidget):

    def __init__(self, file):
        super(Test, self).__init__()
        self.counter = 0
        self.readTestFile(file)
        self.initUI()

    def initUI(self):
        self.text = "Click on Red Circles"
        #self.setGeometry(0, 0, 1500, 800)
        self.showMaximized()
        self.setWindowTitle("Fitts's Law Test")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.show()

    def readTestFile(self, file):
        fobj = open(file, "r")
        for line in fobj:
            line = line.strip()
            vals = line.split(":")
            if(vals[0] == "USER"):
                self.id = vals[1]
            elif(vals[0] == "WIDTHS"):
                self.widths = vals[1].split(",")
            elif(vals[0] == "DISTANCES"):
                self.dists = vals[1].split(",")
        fobj.close()

    def startTest(self):
        self.start = True

    def mousePressEvent(self, event):
        p = event.globalPos()
        #print p
        print "X: "+str(p.x())+", Y: "+str(p.y())
        x1 = self.posX
        x2 = self.posX + self.radius
        y1 = self.posY
        y2 = self.posY + self.radius
        print "x1: "+str(x1)+", x2: "+str(x2)+", y1: "+str(y1)+", y2: "+str(y2)
        if((p.x() >= x1 and p.x() <= x2) and (p.y() >= y1 and p.y() <= y2)):
            print "in Circle"

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        self.drawCircle(event, qp, 10, 20, 50)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 32))
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, "Click on circle!")

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
