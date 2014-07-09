#!/usr/bin/env python
# coding: utf-8

import wiimote
import time
import sys
import csv

wm = wiimote.connect(sys.argv[1])

filename = raw_input("Testfile: ")
xp = yp = zp = 0
data = []


def writeLogData(data):
    csv.register_dialect('logging', delimiter=';', quoting=csv.QUOTE_ALL)
    logfile = open(filename+".csv", "wb")
    writer = csv.DictWriter(logfile, ["x", "y", "z"], 'logging')
    writer.writeheader()
    writer.writerows(data)
    logfile.close()

while True:
    if wm.buttons["A"]:
        x, y, z = wm.accelerometer
        if (x != xp) or (y != yp) or (z != zp):
            print("%d,%d,%d") % (x, y, z)
            data.append({"x": x, "y": y, "z": z})
        xp, yp, zp = x, y, z
        time.sleep(0.01)

    if wm.buttons["B"]:
        print
        writeLogData(data)
        break

wm.disconnect()
time.sleep(1)
