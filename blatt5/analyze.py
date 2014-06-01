#!/usr/bin/python
# -*- coding: utf-8 -*-

import wiimote
from PyQt4 import QtGui, QtCore

class Analyze():
 
    def __init__(self, mac_address):
	self.connectWiimote()
	wm = wiimote.connect(mac_address)
    
def main():
    app = QtGui.QApplication(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()