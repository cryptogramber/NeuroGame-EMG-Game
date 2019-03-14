#!/usr/bin/env python
import wave
import matplotlib.pyplot as plt
from scipy.io import wavfile
import pywt
import numpy
import math
import statsmodels.api as sm

samprate,data = wavfile.read('C:\path\to\file.wav')
dataCh1 = data[:,0]

plt.figure(1)
plt.subplot(311)
plt.plot(dataCh1)

cA, cD = pywt.dwt(dataCh1, 'db20', mode='per')
allTogether = pywt.wavedec(dataCh1, 'db20', mode='per')

plt.subplot(312)
plt.plot(cA)
plt.subplot(313)
plt.plot(cD)
plt.draw()

sigma = sm.robust.scale.stand_mad(allTogether[-1])
uthresh = sigma*numpy.sqrt(10*numpy.log(len(dataCh1)))
denoised = allTogether[:]
denoised[1:] = (pywt.thresholding.soft(i, value=uthresh) for i in denoised[1:])
signal = pywt.waverec(denoised, 'db20', mode='per')

plt.figure(2)
plt.subplot(211)
plt.plot(dataCh1)
plt.subplot(212)
plt.plot(signal)
plt.show()