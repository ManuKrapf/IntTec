#!/usr/bin/python
# -*- coding: utf-8 -*-

import wiimote
from PyQt4 import QtGui, QtCore

class Analyze():
 
    def __init__(self):
	self.connectWiimote()
	addr, name = wiimote.find()
	wm = wiimote.connect(addr)
    
def main():


if __name__ == '__main__':
    main()