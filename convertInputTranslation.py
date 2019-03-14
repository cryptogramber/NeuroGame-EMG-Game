#!/usr/bin/env python
# convertInputTranslation.py 

import math
import numpy
import array as pyarray
from StringIO import StringIO
from array import array

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
class convertInputTranslation:
    def __init__(self):
        # suggested increments:
        #  gain = 1
        #  slope = 0.002
        #  offset = maxEMG/50
        self.gain = 1
        self.slope = .05
        self.xoffset = 0
        self.maxEMG = 256
        self.mouseLUT = pyarray.array("f")
        self.SetParams(self.gain, self.slope, self.xoffset, self.maxEMG)

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def SetParams(self, gain, slope, xoffset, maxEMG):
        self.gain = gain
        self.slope = slope
        self.xoffset = xoffset
        self.maxEMG = maxEMG
        self.mouseLUT = pyarray.array("f")
        for x in range(0,maxEMG):
            self.mouseLUT.append(gain*self.Sigmoid(((x-maxEMG/2)-xoffset)*slope))
        
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def Convert(self, EMGval_ch1, EMGval_ch2):
        if EMGval_ch1 < 0:             EMGval_ch1 = 0
        if EMGval_ch1 >= self.maxEMG:  EMGval_ch1 = self.maxEMG-1
        if EMGval_ch2 < 0:             EMGval_ch2 = 0
        if EMGval_ch2 >= self.maxEMG:  EMGval_ch2 = self.maxEMG-1
        return self.mouseLUT[EMGval_ch2] - self.mouseLUT[EMGval_ch1]

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def Sigmoid(self, val):
        return 1/(1+math.exp(-val)) 


