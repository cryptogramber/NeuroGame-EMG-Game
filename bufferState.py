#!/usr/bin/env python
# bufferState.py 
from numpy import *

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
class bufferState:
    def __init__(self, numChannels, numframes):
        self.numChannels = numChannels
        self.numframes = numframes
        self.start = 0
        self.end = 0
        self.wrapped = 0
        self.data = [[0 for col in range(numChannels)] for row in range(numframes)]

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def clear(self):
        self.start = 0
        self.end = 0
        self.wrapped = 0

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def put(self, frame):
        self.data[self.end] = frame
        self.end += 1
        
        if self.end >= self.numframes:
            self.end = 0
            self.wrapped = 1     

        if self.end == self.start:
            self.start +=1
            if self.start >= self.numframes:
                self.start = 0

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def get(self):
        if self.start == self.end:
            return []

        x = self.data[self.start]
        self.start += 1

        if self.start >= self.numframes:
                self.start = 0

        return x

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~       
    def getall(self):
        ar = []
        x = get()
        while x :
            ar.append(x)
        return ar

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def peek(self, framenum):
        if self.start == self.end:
            return []
        return self.data[self.start]

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def mean(self):
        if not self.wrapped:
            a = array(self.data[self.start:self.end])
        else:
            a = array(self.data)
            
        return a.mean(0)

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def median(self):
        if not self.wrapped:
            a = array(self.data[self.start:self.end])
        else:
            a = array(self.data)
            
        if not a.any():
            return []

        if len(a) == 1:
            return a

        a.sort(0)
        lena = len(a)
        half = int(lena/2)
        
        if lena % 2:
            return a[half]
        else:
            return (a[half-2] + a[half-1]) / 2
        

    


