#!/usr/bin/env python
# mvcUserGauge.py

import wx
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab
from array import array

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
class mvcFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.shown = False
        
        self.lastvalid = [0.0,0.0]
        self.data = [array("f"), array("f")]
        self.ymin = 0
        self.maxImageWidth = 324 #324 x 187
        self.maxImageHeight = 187     
        self.placeholder = wx.StaticText(self, -1, ' ')
        self.placeholder2 = wx.StaticText(self, -1, ' ')
        self.instructions = wx.StaticText(self, -1, ' ')
        self.instructions2 = wx.StaticText(self, -1, ' ')
        self.Image = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(self.maxImageWidth, self.maxImageHeight))
        
        self.meterGrey = wx.Image("./images/meter.png", wx.BITMAP_TYPE_PNG)
        self.meterA = wx.Image("./images/meter_a.png", wx.BITMAP_TYPE_PNG)
        self.meterB = wx.Image("./images/meter_b.png", wx.BITMAP_TYPE_PNG)
        self.meterC = wx.Image("./images/meter_c.png", wx.BITMAP_TYPE_PNG)
        self.meterD = wx.Image("./images/meter_d.png", wx.BITMAP_TYPE_PNG)
        self.meterE = wx.Image("./images/meter_e.png", wx.BITMAP_TYPE_PNG)
        self.meterF = wx.Image("./images/meter_f.png", wx.BITMAP_TYPE_PNG)
        self.meterG = wx.Image("./images/meter_g.png", wx.BITMAP_TYPE_PNG)

        self.__set_properties()
        self.__do_layout()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def __set_properties(self):
        self.SetTitle("Muscle Contraction Test")
        self.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.SetMinSize((500, 450))
        self.instructions.SetFont(wx.Font(30, wx.NORMAL, wx.NORMAL, wx.BOLD))
        self.instructions2.SetFont(wx.Font(20, wx.NORMAL, wx.NORMAL, wx.NORMAL))

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def __do_layout(self):
        mainGrid = wx.GridSizer(1, 1, 0, 0)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.placeholder, 0, wx.ALL, 10)
        sizer_1.Add(self.instructions, 0, wx.LEFT|wx.RIGHT, 50)
        sizer_1.Add(self.placeholder2, 0, wx.ALL, 10)
        sizer_1.Add(self.instructions2, 0, wx.LEFT|wx.RIGHT, 50)
        sizer_1.Add(self.Image, 0, wx.ALIGN_CENTER|wx.TOP, 60)
        mainGrid.Add(sizer_1, 0, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def OnClose(self, event):
        self.shown = False
        self.Show(False)

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~     
    def add_data(self, data, channel):
        for i in range(len(data)): 
            if data[i]:  
                self.data[channel].append(float(data[i]))
            else:
                if len(self.data[channel]):
                   self.data[channel].append(self.data[channel][-1])
                else:
                    print "last valid[channel] in add_data mvcUserGauge"
                    self.data[channel].append(self.lastvalid[channel]) 

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~               
    def clear_channel(self,channel):
        self.lastvalid[channel] = self.data[channel][-1]
        self.data[channel] = array("f")

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def draw(self):
       self.draw_channel(0)

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def width(self):
        panesize = self.panel_1.GetSize()
        return panesize[0]

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def draw_channel(self, chan):
        qrs = np.array(self.data[chan])
        if (qrs[0] < 10):
            self.Image.SetBitmap(wx.BitmapFromImage(self.meterA))
        elif (qrs[0] < 20):
            self.Image.SetBitmap(wx.BitmapFromImage(self.meterB))
        elif (qrs[0] < 30):
            self.Image.SetBitmap(wx.BitmapFromImage(self.meterC))
        elif (qrs[0] < 40):
            self.Image.SetBitmap(wx.BitmapFromImage(self.meterD))
        elif (qrs[0] < 50):
            self.Image.SetBitmap(wx.BitmapFromImage(self.meterE))
        elif (qrs[0] < 60):
            self.Image.SetBitmap(wx.BitmapFromImage(self.meterF))
        elif (qrs[0] > 80):
            self.Image.SetBitmap(wx.BitmapFromImage(self.meterG))

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def relax_time(self, chan):
        self.Image.SetBitmap(wx.BitmapFromImage(self.meterGrey))

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def config_plot(self, chan, ymax):
        xmax = 1
        xmin = 0
        ymin = self.ymin

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    topframe = (None, -1, "")
    app.SetTopWindow(topframe)
    topframe.Show()
    app.MainLoop()