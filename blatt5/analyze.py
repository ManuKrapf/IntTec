#!/usr/bin/python
# -*- coding: utf-8 -*-

import wiimote
import sys
import pyqtgraph as pg
from pyqtgraph.flowchart import Flowchart
from PyQt4 import QtGui, QtCore


class Analyze(QtGui.QWidget):

    def __init__(self, mac_address):
        super(Analyze, self).__init__()
        self.wm = wiimote.connect(mac_address)
        self.initFlowchart()
        self.getData() # get accelerometer data to plot
        self.plotData()

    def initFlowchart(self):
        fc = Flowchart(terminals={
            'nameOfInputTerminal': {'io': 'in'},
            'nameOfOutputTerminal': {'io': 'out'}
        })
        ctrl = fc.ctrlWidget()
        #self.addWidget(ctrl)

        fc.setInput(self.wm.accelerometer)
        output = fc.output()
        output = fc.process(nameOfInputTerminal="newValue")

    def getData(self):
        self.data = self.wm.accelerometer

    def plotData(self, data1, data2, data3):
        win = pg.GraphicsWindow()  # Automatically generates grids with multiple items
        win.addPlot(self.data[0], row=0, col=0)
        win.addPlot(self.data[1], row=0, col=1)
        win.addPlot(self.data[2], row=1, col=0, colspan=2)
        pg.show(self.data)  # imageData must be a numpy array with 2 to 4 dimensions

def main():
    app = QtGui.QApplication(sys.argv)
    analyze = Analyze(sys.argv[1])
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()