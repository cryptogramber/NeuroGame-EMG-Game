#!/usr/bin/env python
import wx

class MyDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_5 = wx.StaticText(self, -1, "Turn on the NeuroGame box.", style=wx.ALIGN_CENTRE)
        self.bitmap_1 = wx.StaticBitmap(self, -1, wx.Bitmap("./images/5_power_big.JPG", wx.BITMAP_TYPE_ANY))
        self.button_3 = wx.Button(self, -1, "<< Back")
        self.button_4 = wx.Button(self, -1, "Finish")
        self.panel_2 = wx.Panel(self, -1)
        self.button_5 = wx.Button(self, -1, "Exit")
        self.Bind(wx.EVT_BUTTON, self.Back, self.button_3)
        self.Bind(wx.EVT_BUTTON, self.Next, self.button_4)
        self.Bind(wx.EVT_BUTTON, self.Exit, self.button_5)
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("Power On NeuroGame Box")
        self.SetBackgroundColour(wx.Colour(240, 240, 240))
        self.label_5.SetFont(wx.Font(14, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "Arial"))
        self.button_3.SetFont(wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Arial"))
        self.button_4.SetFont(wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Arial"))
        self.button_5.SetFont(wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Arial"))

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1 = wx.GridSizer(1, 4, 0, 0)
        sizer_1.Add(self.label_5, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 20)
        sizer_1.Add(self.bitmap_1, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 20)
        grid_sizer_1.Add(self.button_3, 0, wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_1.Add(self.button_4, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_1.Add(self.panel_2, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(self.button_5, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_1.Add(grid_sizer_1, 1, wx.ALL|wx.EXPAND, 20)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        self.Centre()

    def Back(self, event):
        self.EndModal(wx.ID_BACKWARD)

    def Next(self, event):
        self.EndModal(wx.ID_EXIT)

    def Exit(self, event):
        self.EndModal(wx.ID_EXIT)

if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    dialog_1 = MyDialog(None, -1, "")
    app.SetTopWindow(dialog_1)
    dialog_1.Show()
    app.MainLoop()