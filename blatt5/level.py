#!/usr/bin/python
# -*- coding: utf-8 -*-

import wiimote
from PyQt4 import QtGui, QtCore

class BubbleLevel():
 
    def __init__(self, mac_adress):
	wm = wiimote.connect(mac_address)
	self.measureInclination()

    def measureInclination(self):
	"""
	mittels accelerometer Abweichung von x/y-Achse messen
        Richtung und Grad der Abweichung auf den LEDs anzeigen 
	(versteh ich nicht ganz wie das gehen soll)
	wenn Abweichung = 0 (Wiimote genau auf x/y-Achse), evtl mit while Schleife:
	"""	
	
	"""
	WiiMote vibriert und alle LEDs leuchten
	"""
	wm.rumble(0.1)
	for x in range(0,4):
	    wm.leds[x] = True
    
def main():
    app = QtGui.QApplication(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()