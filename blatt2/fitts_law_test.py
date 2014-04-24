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
        self.setGeometry(0, 0, 1500, 800)
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


def main():
    file = raw_input("Testfile: ")
    app = QtGui.QApplication(sys.argv)
    test = Test(file)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
