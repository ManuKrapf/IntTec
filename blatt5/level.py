#!/usr/bin/python
# -*- coding: utf-8 -*-

import wiimote
import sys
import time


class BubbleLevel(object):

    def __init__(self, macaddress):
        self.wm = wiimote.connect(macaddress)
        self.measureInclination()

    def measureInclination(self):
        xorigin = 512
        yorigin = 510
        offset = 2
        axis = "x"
        while(True):
            self.resetLED()
            if(self.wm.buttons['Home']):
                sys.exit("exit")
            if(self.wm.buttons['Up']) or (self.wm.buttons['Right']):
                axis = "x"
                print("Measuring the x Axis!")
            if(self.wm.buttons['Down']) or (self.wm.buttons['Left']):
                axis = "y"
                print("Measuring the y Axis!")
            acc = self.wm.accelerometer
            if(axis == "x"):
                x = acc[0]
                print("X: "+str(x))
                if(x in range((xorigin-offset), (xorigin+offset))):
                    self.isPerfect()
                else:
                    self.showDeviation(x, xorigin)
            elif(axis == "y"):
                y = acc[1]
                print("Y: "+str(y))
                if(y in range((yorigin-offset), (yorigin+offset))):
                    self.isPerfect()
                else:
                    self.showDeviation(y, yorigin)
            time.sleep(0.5)

    def showDeviation(self, val, origin):
        if(val < origin):
            self.wm.leds[1] = True
            if(val < (origin-50)):
                self.wm.leds[0] = True
        elif(val > origin):
            self.wm.leds[2] = True
            if(val > (origin+50)):
                self.wm.leds[3] = True

    def isPerfect(self):
        self.wm.rumble(1)
        self.wm.leds[0] = True
        self.wm.leds[1] = True
        self.wm.leds[2] = True
        self.wm.leds[3] = True

    def resetLED(self):
        self.wm.leds[0] = False
        self.wm.leds[1] = False
        self.wm.leds[2] = False
        self.wm.leds[3] = False


def main():
    bubble = BubbleLevel(sys.argv[1])

if __name__ == '__main__':
    main()