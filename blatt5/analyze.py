#!/usr/bin/python
# -*- coding: utf-8 -*-

import wiimote
import pyqtgraph as pg
from pyqtgraph.flowchart import Flowchart
from PyQt4 import QtGui, QtCore

class Analyze():
 
    def __init__(self, mac_address):
	wm = wiimote.connect(mac_address)
	self.initFlochart()
	self.getData() # get accelerometer data to plot
	self.plotData()

    def initFlowchart(self):
	fc = Flowchart(terminals={
    	    'nameOfInputTerminal': {'io': 'in'},
    	    'nameOfOutputTerminal': {'io': 'out'}
	})
	ctrl = fc.ctrlWidget()
	myLayout.addWidget(ctrl)

	fc.setInput(""" accelerometer data """)
	output = fc.output()
	output = fc.process(nameOfInputTerminal=newValue)

    def getData(self):
	
    
    def plotData(self, data1, data2, data3):
	win = pg.GraphicsWindow()  # Automatically generates grids with multiple items
	win.addPlot(data1, row=0, col=0)
	win.addPlot(data2, row=0, col=1)
	win.addPlot(data3, row=1, col=0, colspan=2)

pg.show(imageData)  # imageData must be a numpy array with 2 to 4 dimensions
    
def main():
    app = QtGui.QApplication(sys.argv)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()