#!/usr/bin/env python
# coding: utf-8
# -*- coding: utf-8 -*-

import sys
import wiimote

class DataRec(object):

    def __init__(self):
        super(DataRec, self).__init__()

    def getFFT(self, y, Fs):
        """
        Calcs the FFT for the given values with a given Frequency
        """
        n = len(y)  # length of the signal
        k = arange(n)
        T = n/Fs
        frq = k/T  # two sides frequency range
        frq = frq[range(n/2)]  # one side frequency range

        Y = fft(y)/n  # fft computing and normalization
        Y = Y[range(n/2)]

        for i in range(0, len(Y)-1):
            Y[i] = abs(Y[i])

        return Y  # self.getSquareSignal(Y)