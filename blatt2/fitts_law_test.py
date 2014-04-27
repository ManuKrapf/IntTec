#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import itertools
import random
import csv
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
        self.show()
        self.center = QtCore.QPoint(self.width() / 2, self.height() / 2)

    def initTest(self):
        self.combs = 4 * list(itertools.product(self.dists, self.widths))
        random.shuffle(self.combs)
        self.results = []
        self.timeobj = QtCore.QTime()
        self.startTest()

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
        currtime = QtCore.QDateTime.currentDateTime()
        self.timestamp = str(currtime.toString(QtCore.Qt.DateFormat(1)))
        self.startmeasure = True
        self.setMouseTracking(True)

    def nextTest(self):
        self.counter += 1
        if(self.counter < len(self.combs)):
            testvals = self.combs[self.counter]
            self.start = self.target
            if(self.counter % 2) == 0:
                #target right
                tx = self.start.x() + int(int(testvals[0])/2)
                if tx > (self.width() - int(max(self.widths))):
                    tx = self.start.x() - int(int(testvals[0])/2)
            else:
                #target left
                tx = self.start.x() - int(int(testvals[0])/2)
                if tx < (0 + int(max(self.widths))):
                    tx = self.start.x() + int(int(testvals[0])/2)
            y = self.center.y()
            self.target = QtCore.QPoint(tx, y)
            self.radius = int(int(testvals[1])/2)
            currtime = QtCore.QDateTime.currentDateTime()
            self.timestamp = str(currtime.toString(QtCore.Qt.DateFormat(1)))
            self.startmeasure = True
        else:
            self.endTest()
        self.repaint()

    def endTest(self):
        self.writeLogData()
        self.start = False

    def mousePressEvent(self, event):
        if(self.start):
            p = event.pos()
            x1 = self.target.x() - self.radius
            x2 = self.target.x() + self.radius
            y1 = self.target.y() - self.radius
            y2 = self.target.y() + self.radius
            if((p.x() >= x1 and p.x() <= x2) and
                    (p.y() >= y1 and p.y() <= y2)):
                #print "in Circle"
                self.targetClicked(p)

    def targetClicked(self, pos):
        self.time = self.timeobj.elapsed()
        self.offX = pos.x() - self.target.x()
        self.offY = pos.y() - self.target.y()
        self.saveTest()
        self.nextTest()

    def mouseMoveEvent(self, event):
        if self.startmeasure:
            self.pointerpos = str(event.pos().x())+","+str(event.pos().y())
            self.timeobj.start()
            self.startmeasure = False

    def saveTest(self):
        data = {
            "user": self.id,
            "timestamp": self.timestamp,
            "distance": self.combs[self.counter][0],
            "widths": self.combs[self.counter][1],
            "time": self.time,
            "trial": self.counter,
            "pos_pointer": self.pointerpos,
            "pos_target": str(self.target.x())+","+str(self.target.y()),
            "moffset-x": self.offX,
            "moffset-y": self.offY
        }
        print data
        self.results.append(data)

    def writeLogData(self):
        csv.register_dialect('logging', delimiter=';', quoting=csv.QUOTE_ALL)
        logfile = open("user"+str(self.id)+".csv", "wb")
        writer = csv.DictWriter(logfile, ["user", "timestamp", "trial",
                                "distance", "widths", "time", "pos_pointer",
                                          "pos_target", "moffset-x",
                                          "moffset-y"], 'logging')
        writer.writeheader()
        writer.writerows(self.results)
        logfile.close()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if(self.start):
            self.drawText(event, qp,
                          "Click on red circle: "+str(self.counter)+"/64")
            self.drawStart(event, qp)
            self.drawTarget(event, qp)
        else:
            self.drawText(event, qp, "Test finished!")
        qp.end()

    def drawText(self, event, qp, text):
        qp.setPen(QtGui.QColor(168, 34, 3))
        qp.setFont(QtGui.QFont('Decorative', 32))
        qp.drawText(event.rect(), QtCore.Qt.AlignHCenter, text)

    def drawStart(self, event, qp):
        qp.setBrush(QtGui.QColor(34, 34, 200))
        qp.drawEllipse(self.start, 10, 10)

    def drawTarget(self, event, qp):
        qp.setBrush(QtGui.QColor(200, 34, 34))
        qp.drawEllipse(self.target, self.radius, self.radius)


def main():
    file = raw_input("Testfile: ")
    #file = "test.txt"
    app = QtGui.QApplication(sys.argv)
    test = Test(file)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
