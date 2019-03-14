#!/usr/bin/env python
# adminOScope.py 

import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab
from array import array
matplotlib.rc('axes',edgecolor='w')

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
class ScopeFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        self.panel_2 = wx.Panel(self, -1)
        self.__set_properties()
        self.__do_layout()
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.shown = False
        self.data = [array("f"), array("f")]
        self.ymin = 0
        self.ymax = 255
        self.fig = [0,0]
        self.axes = [0,0]
        self.canvas = [0,0]
        self.plot_data = [0,0]
        self.lastvalid = [0.0, 0.0]
        self.init_scope_panels()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def __set_properties(self):
        self.SetTitle("Neuroplay Scope")
        self.panel_1.SetMinSize((600, 300))
        self.panel_2.SetMinSize((600, 300))

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.panel_1, 1, wx.EXPAND | wx.ALL, 0)
        sizer_2.Add(self.panel_2, 1, wx.EXPAND | wx.ALL, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnClose(self, event):
        print "Closing scope window."
        self.shown = False
        self.Show(False)

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def init_scope_panels(self):
        for chan in range(0,2):
            #self.fig[chan] = Figure((6.0, 2.8), dpi=100)
            self.fig[chan] = Figure((6.0, 3.0), dpi=100, facecolor='k', edgecolor='k')
            self.axes[chan] = self.fig[chan].add_subplot(111)
            self.axes[chan].set_axis_bgcolor('black')
            pylab.setp(self.axes[chan].get_xticklabels(), fontsize=8, color='w')
            pylab.setp(self.axes[chan].get_yticklabels(), fontsize=8, color='w')
            #orig #self.plot_data[chan] = self.axes[chan].plot(self.data[chan],linewidth=2,color=(1, 1, 0))[0]

        #plot the data as a line series, and save the reference to the plotted line series
        self.plot_data[0] = self.axes[0].plot(self.data[0],linewidth=1,color=(0, 0, 1))[0]
        self.plot_data[1] = self.axes[1].plot(self.data[1],linewidth=1,color=(1, 1, 0))[0]

        self.canvas[0] = FigCanvas(self.panel_1, -1, self.fig[0])
        self.canvas[1] = FigCanvas(self.panel_2, -1, self.fig[1])
        self.axes[0].set_title("Right Channel 1 (Blue)", size=12, color='w')
        self.axes[1].set_title("Left Channel 2 (Yellow)", size=12, color='w')

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-
    def add_data(self, data, channel):
        for i in range(len(data)): 
            if data[i]:  
                self.data[channel].append(float(data[i]))
            else:
                if len(self.data[channel]):
                   self.data[channel].append(self.data[channel][-1])
                else:
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
        self.draw_channel(1)

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def width(self):
        panesize = self.panel_2.GetSize()
        return panesize[0]

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def draw_channel(self, chan):
        #endpos = min(len(self.data[0]), len(self.data[1]))
        endpos = len(self.data[chan])
        startpos = max(0,endpos - self.width())

        xmax = endpos
        xmin = startpos
        ymin = self.ymin
        ymax = self.ymax

        self.axes[chan].set_xbound(lower=xmin, upper=xmax)
        self.axes[chan].set_ybound(lower=ymin, upper=ymax)
        self.axes[chan].grid(False)
                 
        self.plot_data[chan].set_xdata(np.arange(len(self.data[chan])))
        self.plot_data[chan].set_ydata(np.array(self.data[chan]))
        self.canvas[chan].draw()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    topframe = (None, -1, "")
    app.SetTopWindow(topframe)
    topframe.Show()
    app.MainLoop()
