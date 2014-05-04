#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re


class Klmcalc(object):

    def __init__(self, file):
        super(Klmcalc, self).__init__()
        self.kTime = 280
        self.kCount = 0
        self.pTime = 1100
        self.pCount = 0
        self.bTime = 100
        self.bCount = 0
        self.hTime = 400
        self.hCount = 0
        self.mTime = 1200
        self.mCount = 0
        self.readFile(file)
        self.calcTime()

    def readFile(self, file):
        fobj = open(file, "r")
        for line in fobj:
            line = line.strip()
            if not (line.startswith("#")):
                self.checkLine(line)
        fobj.close()

    def checkLine(self, line):
        splits = line.split("#")
        opstring = splits[0].replace(" ", "")
        operators = re.findall("[0-9]*[a-zA-Z]", opstring)
        for val in operators:
            count = 1
            op = ""
            if(len(val) > 1):
                count = int(val[0:len(val)-1])
                op = val[len(val)-1:len(val)]
            else:
                op = val
            self.addValue(count, op.lower())

    def addValue(self, count, op):
        if op == "k":
            self.kCount += count
        elif op == "p":
            self.pCount += count
        elif op == "b":
            self.bCount += count
        elif op == "h":
            self.hCount += count
        elif op == "m":
            self.mCount += count

    def calcTime(self):
        k = self.kCount * self.kTime
        p = self.pCount * self.pTime
        b = self.bCount * self.bTime
        h = self.hCount * self.hTime
        m = self.mCount * self.mTime
        self.time = float(k+p+b+h+m)/1000
        s = "The prediction for the task completion time is "
        print s + str(self.time) + "s"


def main():
    if(len(sys.argv) > 1):
        file = sys.argv[1]
    else:
        file = raw_input("File: ")
    #file = "test.txt"
    calc = Klmcalc(file)
    #sys.exit(app.exec_())


if __name__ == '__main__':
    main()
