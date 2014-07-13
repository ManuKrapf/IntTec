#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

from pyqtgraph.flowchart import Node
import pyqtgraph.flowchart.library as fclib
from scipy import fft
from sklearn import svm
import numpy as np
import types


class SvmClassifierNode(Node):

    nodeName = "SVMNode"

    def __init__(self, name):
        terminals = {
            'categories': dict(io='in'),
            'trainigData': dict(io='in'),
            'classifyData': dict(io='in'),
            'classification': dict(io='out'),
        }
        Node.__init__(self, name, terminals=terminals)

    def makeCategories(self, carr):
        cats = []
        for c in carr:
            cats.append(carr.index(c))
        return cats

    def classify(self, categories, train, classdata):
        cats = self.makeCategories(categories)
        svc = svm.SVC()
        svc.fit(train, cats)
        cat = svc.predict(classdata)
        print cat
        return categories[cat]

    def process(self, **kwds):
        cdata = [[kwds['classifyData'][:len(kwds['trainigData'][0])]]]
        print cdata
        output = self.classify(kwds['categories'],
                               kwds['trainigData'],
                               cdata)
        return {
            'classification': output
            }

fclib.registerNodeType(SvmClassifierNode, [('Data',)])


class FFTNode(Node):

    nodeName = "FFTNode"

    def __init__(self, name):
        terminals = {
            'dataIn': dict(io='in'),
            'dataOut': dict(io='out'),
        }
        Node.__init__(self, name, terminals=terminals)

    def calculation(self, data):
        if(isinstance(data[0], types.ListType)):
            freq = [np.abs(fft(l)/len(l))[1:len(l)/2] for l in data]
            freq = [n.tolist() for n in freq]
        else:
            l = data
            freq = np.abs(fft(l)/len(l))[1:len(l)/2]
            #freq = [[v] for v in freq]
            #freq = freq.tolist()
        return freq  # .tolist()

    def process(self, **kwdargs):
        out = self.calculation(kwdargs['dataIn'])
        #print type(out[0])
        return {'dataOut': out}

fclib.registerNodeType(FFTNode, [('Data',)])