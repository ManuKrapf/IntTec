#!/usr/bin/python
# -*- coding: utf-8 -*-

import wiimote
from PyQt4 import QtGui, QtCore

class BubbleLevel():
 
    def __init__(self, mac_adress):
	self.connectWiimote()
	
    def connectWiimote(self):
	addr, name = wiimote.find()
	wm = wiimote.connect(addr)	
	        
    
def main():


if __name__ == '__main__':
    main()