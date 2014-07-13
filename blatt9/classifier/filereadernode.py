#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

from pyqtgraph.flowchart import Node
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtGui
import numpy as np


class FileReaderNode(Node):

    nodeName = "FileReader"

    def __init__(self, name):
        terminals = {
            'category': dict(io='out'),
            'fileVals': dict(io='out'),
        }
        self.categories = []
        self.data = []
        self.ui = QtGui.QWidget()
        self.layout = QtGui.QGridLayout()
        label = QtGui.QLabel("CSV Filename (without .csv):")
        self.layout.addWidget(label)
        self.text = QtGui.QLineEdit()
        self.layout.addWidget(self.text)
        self.connect_button = QtGui.QPushButton("read file")
        self.layout.addWidget(self.connect_button)
        self.ui.setLayout(self.layout)
        self.file = "sitting2"
        self.text.setText(self.file)
        self.file += ".csv"
        self.connect_button.clicked.connect(self.start_reading)
        Node.__init__(self, name, terminals=terminals)
        self.initialRead()

    def ctrlWidget(self):
        return self.ui

    def initialRead(self):
        self.file = "sitting1.csv"
        self.read_file()
        self.file = "sword1.csv"
        self.read_file()
        self.file = "walking1.csv"
        self.read_file()
        self.update()

    def start_reading(self):
        self.file = str(self.text.text()).strip()+".csv"
        self.read_file()
        self.update()

    def read_file(self):
        readfile = "./data/"+self.file
        x = []
        y = []
        z = []
        avg = []
        for line in open(readfile, "r").readlines():
            _x, _y, _z = map(int,line.strip().split(","))
            x.append(_x)
            y.append(_y)
            z.append(_z)
            avg.append((_x+_y+_z)/3)
        self.categories.append(self.file[:len(self.file)-4])
        self.data.append(avg)
        self.cut_off()

    def cut_off(self):
        all = self.data
        minlen = min([len(x) for x in all])
        self.data = [l[:minlen] for l in self.data]

    def process(self, **kwdargs):
        c = self.categories
        d = self.data
        return {
            'category': c,
            'fileVals': d
            }

fclib.registerNodeType(FileReaderNode, [('Data',)])