#!/usr/bin/env python
# discrete wavelet transform = iteratively transforms a signal of interest into multi-resolution subsets of coefficients
# 1) dwt on MVC to generate detail coefficients
# 2) soft threshold
# 3) standardized median absolute deviation
# 4) recover signal by applying inverse dwt to thresholded coeffients

import wave
import matplotlib.pyplot as plt
from scipy.io import wavfile
import pywt
import numpy
import math
import statsmodels.api as sm

samprate,data = wavfile.read('C:\path\to\file.wav')

dataCh1 = data[:,0]
dataCh2 = data[:,1]

allTogether = pywt.wavedec(dataCh1, 'db20', mode='per')
allTogether2 = pywt.wavedec(dataCh2, 'db20', mode='per')
sigma = sm.robust.scale.stand_mad(allTogether[-1])
sigma2 = sm.robust.scale.stand_mad(allTogether2[-1])
uthresh = sigma*numpy.sqrt(10*numpy.log(len(dataCh1)))
uthresh2 = sigma*numpy.sqrt(10*numpy.log(len(dataCh2)))
denoised = allTogether[:]
denoised2 = allTogether2[:]
denoised[1:] = (pywt.thresholding.soft(i, value=uthresh) for i in denoised[1:])
denoised2[1:] = (pywt.thresholding.soft(i, value=uthresh2) for i in denoised2[1:])
signal = pywt.waverec(denoised, 'db20', mode='per')
signal2 = pywt.waverec(denoised2, 'db20', mode='per')

plt.figure(1)
plt.subplot(211)
plt.plot(dataCh1)
plt.subplot(212)
plt.plot(signal)
plt.draw()

dataCh2_2 = dataCh2 + (dataCh2.T/3)

plt.figure(2)
plt.subplot(211)
plt.plot(dataCh2_2)
plt.subplot(212)
plt.plot(signal2)
plt.show()