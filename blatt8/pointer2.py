#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
import wiimote
import math
import numpy as np

from matplotlib import *


class Pointer(object):

    def __init__(self):
        super(Pointer, self).__init__()
        self.btaddr = "b8:ae:6e:1b:ad:a0"
        self.wm = wiimote.connect(self.btaddr)
        self.ir_vals = []

    def resamplePoints(self, points, n=64):
        I = len(points) / (n-1)
        D = 0
        newpoints = []
        newpoints.append(points[0])
        i = 1
        while(i < len(points)):
            d = self.getDistance(points[i-1], points[i])
            point = [0, 0]
            if((D+d) >= I):
                point[0] = points[i-1][0]+((I-D)/d)*(points[i][0] - points[i-1][0])
                point[1] = points[i-1][1]+((I-D)/d)*(points[i][1] - points[i-1][1])
                newpoints.append(point)
                points.insert(i, point)
                D = 0
            else:
                D = D + d
        return newpoint

    def getDistance(self, p1, p2):
        dist = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
        return dist

    def plotIt(self):
        pass

    def getIrData(self):
        irobj = self.wm.ir
        self.getBiggestVal(irobj)

    def getBiggestVal(self, curr_ir):
        biggest = [0, 0, -1]
        for ir_obj in curr_ir:
            if(biggest[2] < ir_obj["size"]):
                biggest = [ir_obj["x"], ir_obj["y"],
                           ir_obj["size"]]
        if(len(self.ir_vals) >= self.no_avg):
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