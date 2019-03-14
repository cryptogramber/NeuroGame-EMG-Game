#!/usr/bin/env python
# mvcDataHandling.py 

import wx
import wave
import math
import os, sys
import cPickle as pickle
from StringIO import StringIO
from array import array
import pywt as ngwavelet
import time, datetime
import matplotlib.pyplot as plt
import numpy
import statsmodels.api as sm
from scipy.io import wavfile

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
class mvcDataHandling:
    def __init__(self):
        self.started = False
        self.EMGdata = [array('B'), array('B')]
        self.gameName = ''
        self.mouseGain = 0
        self.mousePow = 0
        self.subjectNum = 0
        self.localFilesDir = 'C:\Neurogame' 

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def Start(self, subjectNum, mouseGain, mousePow, sampleRate):
        if self.started:
            self.Stop()

        self.startTime = datetime.datetime.now()
        self.subjectNum = subjectNum
        self.EMGdata = [array('B'), array('B')]
        self.mouseGain = mouseGain
        self.mousePow = mousePow
        self.sampleRate = sampleRate        
        self.started = True

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    # Add new EMG data to bout data buffer, input is string
    def Append_EMG_String(self, datastr, channel):
        self.EMGdata[channel].fromstring(datastr)

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    # Add new EMG data to bout data buffer, input is string
    def Append_EMG_Bytearray(self, bytedata, channel):
        self.EMGdata[channel] += bytedata

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    # Stop recording game bout.
    def Stop(self):        
        self.stoptime = datetime.datetime.now()
        self.started = False

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def saveDataLocally(self,MVCmax,MVCbaseline,chA5xGain,chAGain,chAPGA,chB5xGain,chBGain,chBPGA):
        if self.started:
            self.Stop()
            
        numSamples = min([len(self.EMGdata[0]), len(self.EMGdata[1])])
        numChannels = len(self.EMGdata)
        if not numSamples or not numChannels:
            return

        self.basePath = self.localFilesDir +  '\\Subject_' + str(self.subjectNum)
        if not os.path.exists(self.basePath):
            os.makedirs(self.basePath)

        fnamepath = self.basePath + '\\Subject_' + str(self.subjectNum) + '_MVC_' + self.startTime.strftime('%y%m%d_%H%M%S')
        w = wave.open( fnamepath + '.wav', "w" )
        w.setnchannels( len(self.EMGdata) )
        w.setsampwidth( 1 ) #BYTES
        w.setframerate( self.sampleRate )
        data = array( 'B' )

        for frame in xrange( numSamples ):
            for chan in xrange(numChannels):
               data.append( self.EMGdata[chan][frame])

        w.writeframes( data ) 
        w.close()

        samprate,data = wavfile.read(fnamepath + '.wav',"r")
        dataCh1 = data[:,0]
        dataCh2 = data[:,1]
        allTogether = ngwavelet.wavedec(dataCh1, 'db20', mode='per')
        allTogether2 = ngwavelet.wavedec(dataCh2, 'db20', mode='per')
        sigma = sm.robust.scale.stand_mad(allTogether[-1])
        sigma2 = sm.robust.scale.stand_mad(allTogether2[-1])
        uthresh = sigma*numpy.sqrt(10*numpy.log(len(dataCh1)))
        uthresh2 = sigma*numpy.sqrt(10*numpy.log(len(dataCh2)))
        denoised = allTogether[:]
        denoised2 = allTogether2[:]
        denoised[1:] = (ngwavelet.thresholding.soft(i, value=uthresh) for i in denoised[1:])
        denoised2[1:] = (ngwavelet.thresholding.soft(i, value=uthresh2) for i in denoised2[1:])
        signal = ngwavelet.waverec(denoised, 'db20', mode='per')
        signal2 = ngwavelet.waverec(denoised2, 'db20', mode='per')

        plt.figure(1)
        plt.subplot(211)
        plt.plot(dataCh1)
        plt.subplot(212)
        plt.plot(signal)
        plt.draw()

        plt.figure(2)
        plt.subplot(211)
        plt.plot(dataCh2)
        plt.subplot(212)
        plt.plot(signal2)
        plt.show()

        textfile = open(fnamepath + '.txt', "w")
        textfile.write("{\n")
        textfile.write("\"userid\":\"%d\",\n" % int(self.subjectNum))
        textfile.write("\"ch_a_5x_gain\":\"%f\",\n" % chA5xGain)
        textfile.write("\"ch_a_filter_gain\":\"%f\",\n" % chAGain)
        textfile.write("\"ch_a_pga_index\":\"%f\",\n" % chAPGA)
        textfile.write("\"ch_b_5x_gain\":\"%f\",\n" % chB5xGain)
        textfile.write("\"ch_b_filter_gain\":\"%f\",\n" % chBGain)
        textfile.write("\"ch_b_pga_index\":\"%f\",\n" % chBPGA)
        textfile.write("\"baseline_a\":\"%f\",\n" % MVCbaseline[0][0])
        textfile.write("\"baseline_b\":\"%f\",\n" % MVCbaseline[1][0])
        textfile.write("\"mvc_a\":[[mvc_a1,%f],[mvc_a2," %MVCmax[0][0])
        textfile.write("%f],[mvc_a3," %MVCmax[0][1])
        textfile.write("%f]],\n" %MVCmax[0][2])
        textfile.write("\"mvc_b\":[[mvc_b1,%f],[mvc_b2," %MVCmax[1][0])
        textfile.write("%f],[mvc_b3," %MVCmax[1][1])
        textfile.write("%f]],\n" %MVCmax[1][2])
        textfile.write("}")
        textfile.close()