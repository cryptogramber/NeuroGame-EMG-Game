#!/usr/bin/env python
# NeuroGamePrime.py

import wx, time, datetime, os, sys                 
import math, numpy, pythoncom, pyHook                
import cPickle as pickle                
import serial, threading, re            
import array as pyarray                 
import pywt, userEvent                          
from bufferState import *                
import configGame, gameSession                      
import mvcDataHandling, mvcUserGauge                        
import userInputMonitor, convertInputTranslation                        
import reminderBeginning, reminderEnd                       
import adminInterface, adminOScope
import wxSerialConfigDialog1            
import win32com.client
import _winreg as winreg
import wiiuse, ctypes, wiimoteControl, itertools
import userSetup1, userSetup2, userSetup3, userSetup4, userSetup5, userSetup6, userSetup7
import systemSetup1, systemSetup2, systemSetup3, systemSetup4, systemSetup5

ID_CONNECT_SETTINGS = wx.NewId()
ID_EMG_SCOPE        = wx.NewId()
ID_CONFIG_GAMES     = wx.NewId()
ID_CONFIG_EMG2MOUSE = wx.NewId()
ID_CONFIG_USER      = wx.NewId()
ID_CONFIG_SERVER    = wx.NewId()
ID_CONFIG_HELP      = wx.NewId()
NEWLINE_CR          = 0
NEWLINE_LF          = 1
NEWLINE_CRLF        = 2
SERIALRX            = wx.NewEventType()
EVT_SERIALRX        = wx.PyEventBinder(SERIALRX, 0)        

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
class SerialRxEvent(wx.PyCommandEvent):
    eventType = SERIALRX
    def __init__(self, windowID, data):
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
        self.data = data
    def Clone(self):
        self.__class__(self.GetId(), self.data)
pass

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~  
class MyFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX|wx.SYSTEM_MENU|wx.SIMPLE_BORDER|wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)
        self.welcomelogo = wx.StaticBitmap(self, -1, wx.Bitmap("./images/logo.png", wx.BITMAP_TYPE_ANY))
        self.selectplayerID = wx.ComboBox(self, -1, choices=["NeuroGame wEMG"], style=wx.CB_DROPDOWN)
        self.wiringHelp = wx.BitmapButton(self, -1, wx.Bitmap("./images/compandwiring.png", wx.BITMAP_TYPE_ANY), style=wx.NO_BORDER)
        self.electrodeHelp = wx.BitmapButton(self, -1, wx.Bitmap("./images/electrodeplace.png", wx.BITMAP_TYPE_ANY), style=wx.NO_BORDER)
        self.connectDevice = wx.BitmapButton(self, -1, wx.Bitmap("./images/ngconnect.png", wx.BITMAP_TYPE_ANY), style=wx.NO_BORDER)
        self.statusbar = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_LINEWRAP)
        self.calibrateEMG = wx.BitmapButton(self, -1, wx.Bitmap("./images/muscontract_active.png", wx.BITMAP_TYPE_ANY), style=wx.NO_BORDER)
        self.selectGameText = wx.StaticText(self, -1, "Select Game:")
        self.gameSelection = wx.ComboBox(self, -1, choices=[], style=wx.CB_DROPDOWN)
        self.selectdevicetext = wx.StaticText(self, -1, "Select Player ID:")
        self.selectgamedevice = wx.ComboBox(self, -1, choices=["Player 99"], style=wx.CB_DROPDOWN)
        self.beginGameplay = wx.BitmapButton(self, -1, wx.Bitmap("./images/playbig.png", wx.BITMAP_TYPE_ANY), style=wx.NO_BORDER)
        self.finishGameplay = wx.BitmapButton(self, -1, wx.Bitmap("./images/finishexit.png", wx.BITMAP_TYPE_ANY), style=wx.NO_BORDER)

        self.__set_properties()
        self.__do_layout()
        self.Bind(wx.EVT_BUTTON, self.ComputerWiringHelp, self.wiringHelp)
        self.Bind(wx.EVT_BUTTON, self.OnButtonTestDongle, self.electrodeHelp)
        self.Bind(wx.EVT_BUTTON, self.OnButtonConnect, self.connectDevice)
        self.Bind(wx.EVT_BUTTON, self.OnCalibrateEMG, self.calibrateEMG)
        self.Bind(wx.EVT_TEXT, self.OnTextSelGame, self.gameSelection)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnTextEnterSelGame, self.gameSelection)
        self.Bind(wx.EVT_COMBOBOX, self.OnComboBoxSelGame, self.gameSelection)
        self.Bind(wx.EVT_BUTTON, self.OnButtonStartGame, self.beginGameplay)
        self.Bind(wx.EVT_BUTTON, self.OnButtonDonePlaying, self.finishGameplay)
        self.Bind(EVT_SERIALRX, self.OnSerialRead)              # serial events
        self.Bind(wx.EVT_CHAR, self.OnChar)                     # keyboard events
        self.Bind(wx.EVT_CLOSE, self.OnClose)                   # exit program event
        self.Bind(wx.EVT_NAVIGATION_KEY, self.onNavigate)       

        self.LoadGameConfigs()
        self.gameStarted = False
        self.simEMG = False
        self.mouseHidden = [0,0]
        self.timerUpdatePeriod = 20                             # timer update period in ms
        self.keyValue = 0
        self.mousePosition = [0,0]
        self.mouseCenter = [0,0]
        self.cursorPosition = [0,0]
        self.mouseNull = 0
        self.mouseTest = 0
        self.filesUploaded = False
        self.enabledMouseEMG = 0                                # flag indicating EMG to mouse conversion is enabled

        self.convertInputTranslation = convertInputTranslation.convertInputTranslation()
        self.lastValueEMG = 0
        self.maxEMG = [pyarray.array("f"),pyarray.array("f")]
        self.zcBufEMG = [pyarray.array("f"),pyarray.array("f")]
        self.zcThreshEMG = 20
        self.zcIncrementEMG = .1
        self.zcCurValEMG = 0
        self.mouseMethod = 0                                    # 0 = zero crossing, 1 = max envelope
        self.MVCBaselineInProgress = False
        self.MVCCollectionInProgress = False
        self.MVCTestInProgress = False
        self.MVCRelaxInProgress = False
        self.EMGCalibrationInProgress = False
        self.EMGCalibrationValues = [pyarray.array("f"),pyarray.array("f")]
        self.autocalOnEMG = False
        #self.EMGAutocal_buffer = [pyarray.array("f"),pyarray.array("f")] #314
        self.autocalPeriodEMG = 4
        self.autocalCountEMG = 0
        self.autocalCountEMGThresh = int(self.autocalPeriodEMG*1000/self.timerUpdatePeriod)
        self.keymonitor = userInputMonitor.userInputMonitor()
        self.displaysize = wx.GetDisplaySize()

        #self.smootherbuf_size = 5
        #self.smootherbufpos = 0
        ## ADC serial data mode: 0=binary (x byte, y byte), 1=text ("xavl,yval<CR><LF>")
        #self.ADCmode = 0
        #self.ADCbinarysamplecount = 0
        #self.totalAmtMoved = 0
       
        self.hm = pyHook.HookManager()
        self.hm.MouseMove = self.OnMouseMove
        self.hm.MouseWheel = self.OnMouseWheel
        self.hm.KeyChar = self.OnKeyCharEvent
        self.hm.KeyDown = self.OnKeyDownEvent
        self.hm.KeyUp = self.OnKeyUpEvent
        self.hm.HookMouse()                     
        self.hm.HookKeyboard()        
        self.InitSerialPorts();             
      
        self.dialogSerialConfig = wxSerialConfigDialog1.SerialConfigDialog1(None, -1, "",
            show=wxSerialConfigDialog1.SHOW_BAUDRATE|wxSerialConfigDialog1.SHOW_FORMAT|wxSerialConfigDialog1.SHOW_FLOW,
            serial1=self.serial1)
               
        self.scopeWindowEMG = adminOScope.ScopeFrame(None, -1, "" )
        self.scopeWindowMVC = mvcUserGauge.mvcFrame(None, -1, "" )  
        self.scopeDrawCount = 0
        self.scopeInterval = 0
        self.reminderImages = reminderBeginning.MyDialog(None, -1, "")
        self.reminderImagesEnd = reminderEnd.MyDialog(None, -1, "")
        self.systemConfigs = adminInterface.MyDialog(None, -1, "")
        self.userSetup1 = userSetup1.MyDialog(None, -1, "")
        self.userSetup2 = userSetup2.MyDialog(None, -1, "")
        self.userSetup3 = userSetup3.MyDialog(None, -1, "")
        self.userSetup4 = userSetup4.MyDialog(None, -1, "")
        self.userSetup5 = userSetup5.MyDialog(None, -1, "")
        self.userSetup6 = userSetup6.MyDialog(None, -1, "")
        self.userSetup7 = userSetup7.MyDialog(None, -1, "")
        self.systemSetup1 = systemSetup1.MyDialog(None, -1, "")
        self.systemSetup2 = systemSetup2.MyDialog(None, -1, "")
        self.systemSetup3 = systemSetup3.MyDialog(None, -1, "")
        self.systemSetup4 = systemSetup4.MyDialog(None, -1, "")
        self.systemSetup5 = systemSetup5.MyDialog(None, -1, "")
        self.reminderImages.ShowModal()
        self.LoadConfigDefaults()
        self.convertInputTranslation.SetParams(self.systemConfigs.gainEMG, self.systemConfigs.slopeEMG, self.systemConfigs.EMGxoffset, 256)
        self.gameSessionHandler = gameSession.gameSession()                 
        self.collectMVC = mvcDataHandling.mvcDataHandling()   
        self.wiimote = wiimoteControl.wiimoteControl()                
        self.fifobuffer300 = bufferState(1,300)              

        self.CheckSerialStream = False
        if self.CheckSerialStream:
            self.fifobuffer100a = bufferState(1,100)
        self.serialbuffer = pyarray.array('b')              

        self.EMGbuffer = [pyarray.array('B'), pyarray.array('B')]
        self.EMGbuffer2 = [pyarray.array('B'), pyarray.array('B')]
        self.timer = wx.Timer(self, wx.ID_ANY)
        self.timer.Start(self.timerUpdatePeriod) 
        self.Bind(wx.EVT_TIMER, self.OnTimerUpdate, self.timer)

        self.alive2 = threading.Event()
        self.StartWiimoteInput()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def __set_properties(self):
        self.statusbar.AppendText("After connecting your sensor electrodes and turning on the NeuroGame device, press the \"Sync NeuroGame Device\" button to start.\n")  
        self.SetTitle("NeuroGame Prime")
        self.SetBackgroundColour(wx.Colour(255,255,255))
        self.selectplayerID.SetMinSize((170, 26))
        self.selectplayerID.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Consolas"))
        self.selectplayerID.SetSelection(0)
        self.wiringHelp.SetSize(self.wiringHelp.GetBestSize())
        self.electrodeHelp.SetSize(self.electrodeHelp.GetBestSize())
        self.connectDevice.SetBitmapDisabled(wx.Bitmap("./images/dongconnect_inact.png", wx.BITMAP_TYPE_ANY))
        self.connectDevice.SetSize(self.connectDevice.GetBestSize())
        self.statusbar.SetMinSize((400, 83))
        self.statusbar.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.calibrateEMG.SetBitmapDisabled(wx.Bitmap("./images/muscontract_inact.png", wx.BITMAP_TYPE_ANY))
        self.calibrateEMG.SetSize(self.calibrateEMG.GetBestSize())
        self.selectGameText.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Segoe UI Semibold"))
        self.gameSelection.SetMinSize((200, 26))
        self.gameSelection.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Consolas"))
        self.selectdevicetext.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Segoe UI Semibold"))
        self.selectgamedevice.SetMinSize((200, 26))
        self.selectgamedevice.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Consolas"))
        self.selectgamedevice.SetSelection(0)
        self.beginGameplay.SetBitmapDisabled(wx.Bitmap("./images/playbig_inact.png", wx.BITMAP_TYPE_ANY))
        self.beginGameplay.SetSize(self.beginGameplay.GetBestSize())
        self.finishGameplay.SetSize(self.finishGameplay.GetBestSize())
        iconFile = "favicon.ico"
        icon1 = wx.Icon(iconFile, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon1)
        self.selectplayerID.Enable(False)
        self.selectgamedevice.Enable(False)
        self.selectdevicetext.Enable(False)
        self.calibrateEMG.Enable(False)
        self.selectGameText.Enable(False)
        self.gameSelection.Enable(False)
        self.beginGameplay.Enable(False)
        
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def __do_layout(self):
        gridHeaderSizer = wx.GridSizer(1, 2, 0, 0)
        deviceSelSizer = wx.BoxSizer(wx.HORIZONTAL)
        deviceSelSizer.Add((25,1))
        deviceSelSizer.Add(self.selectplayerID, 0, wx.TOP, 50)
        logoSizer = wx.BoxSizer(wx.HORIZONTAL)
        logoSizer.Add(self.welcomelogo, 0, wx.TOP|wx.BOTTOM,15)
        gridHeaderSizer.Add(logoSizer, 0, 0)
        gridHeaderSizer.Add(deviceSelSizer, 0, 0, 0)
        firstSizer = wx.BoxSizer(wx.VERTICAL)
        firstSizer.Add(gridHeaderSizer, 0, wx.LEFT, 15)
        firstSizer.Add(self.wiringHelp, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 15)
        firstSizer.Add(self.electrodeHelp, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 15)
        firstSizer.Add(self.connectDevice, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 15)
        firstSizer.Add(self.statusbar, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        firstSizer.Add(self.calibrateEMG, 0, wx.LEFT|wx.RIGHT|wx.TOP, 15)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_4.Add(self.selectGameText, 0, wx.BOTTOM, 4)
        sizer_4.Add(self.gameSelection, 0, wx.BOTTOM, 4)
        sizer_4.Add(self.selectdevicetext, 0, wx.TOP|wx.BOTTOM, 4)
        sizer_4.Add(self.selectgamedevice, 0, 0, 0)
        sizer_3.Add(sizer_4, 1, 0, 0)
        sizer_3.Add(self.beginGameplay, 0, wx.LEFT|wx.ALIGN_RIGHT, 19)
        firstSizer.Add(sizer_3, 1, wx.ALL, 16)
        firstSizer.Add(self.finishGameplay, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 15)
        self.SetSizer(firstSizer)
        firstSizer.Fit(self)
        self.Layout()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def onNavigate(self, event):
        return True

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def InitSerialPorts(self):
        portNum = 1
        self.serial1 = serial.Serial()
        objSWbemServices = win32com.client.Dispatch("WbemScripting.SWbemLocator").ConnectServer(".","root\cimv2")
        colItems = objSWbemServices.ExecQuery("SELECT * FROM Win32_PnPEntity")
        for objItem in colItems:
            if(objItem.Name!=None and "USB Serial Port" in objItem.Name):
                rxPortString = re.search(r'\(([a-zA-Z]{3}[0-9]{1,3})\)', objItem.Name)
                rxxPortString = rxPortString.group(1)
                rx = re.compile(r'([0-9]{1,3})')
                rxx = rx.search(objItem.Name)
                print('-'*60)
                print("Name: " + objItem.Name)
                print("Status: " + objItem.Status)
                print("Availability: " + `objItem.Availability`)
                print("Manufacturer: " + objItem.Manufacturer)
                print("DeviceID: " + objItem.DeviceID)
                print("COM Port #: " + rxx.group(1))
                portNum = int(rxx.group(1)) - 1
                print("COM Port ID: " + `portNum`)
                print("Port String: " + rxxPortString)
                self.serial1.portstr = rxxPortString            
                self.serial1 = serial.Serial(portNum)

        try:
            self.serial1.timeout = 0.5                         
            self.thread1 = None
            self.alive1 = threading.Event()       
            self.serial1.baudrate = 57600
            self.serial1.bytesize = 8
            self.serial1.stopbits = 1
            self.serial1.rtscts = 0
            self.serial1.xonxoff = 0
            self.serial1.timeout = 0   
            self.serialconnected = 0
        except serial.SerialException, e:
            print "error 1: " + str(e)
            self.serial1 = 1
            self.serialconnected = 0
        
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def LoadGameConfigs(self):
        self.configGames = []
        self.configGames.append(configGame.configGame('Peggle Deluxe',
                                                      "C:\\Program Files (x86)\\PopCap Games\\Peggle Deluxe\\Peggle.exe",
                                                      [""], [""], [""], configGame.mouse_converter(1, 400, -1000, 1000, -700, 700)))

        self.configGames.append(configGame.configGame('Peggle Nights',
                                                      "C:\\Program Files (x86)\\PopCap Games\\Peggle Nights\\PeggleNights.exe",
                                                      [""], [""], [""], configGame.mouse_converter(1, 400, -1000, 1000, -700, 700)))

        self.gameSelection.Clear()
        for game in self.configGames:
            self.gameSelection.Append(game.gameName)   
        self.gameSelection.Select(0)
        self.currentGameConfig = []

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def LoadConfigDefaults(self):
        self.systemConfigs.Load()
        self.dialogSerialConfig.Load()
        self.systemConfigs.Load()
        ok = True

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def SaveConfigDefaults(self):
        self.systemConfigs.Load()
        self.dialogSerialConfig.Save()
        self.systemConfigs.Save()
        ok = True

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnButtonConnect(self, event): 
        if event is not None:                       
            self.StopThread()
            self.serial1.close()
        if self.serialconnected:
            self.statusbar.AppendText("Serial Terminal Closed\n")
            self.StopThread()
            self.serial1.close()
            self.serialconnected = 0
            self.calibrateEMG.Enable(False)
            self.selectGameText.Enable(False)
            self.gameSelection.Enable(False)
            self.beginGameplay.Enable(False)
            self.finishGameplay.Enable(False)
        else:
            openedOK = False
            self.dialogSerialConfig.SetPortsFromContent()
            try:
                self.serial1.open()
            except serial.SerialException, e:
                print "error 1: " + str(e)
                dlg = wx.MessageDialog(None, str(e), "Serial Port Error", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                openedOK = True

            if openedOK:
                self.StartSerialPortThreads()
                self.statusbar.AppendText("Neurogame connected: Serial Terminal on %s [%s, %s%s%s%s%s]" % (
                    self.serial1.portstr,
                    self.serial1.baudrate,
                    self.serial1.bytesize,
                    self.serial1.parity,
                    self.serial1.stopbits,
                    self.serial1.rtscts and ' RTS/CTS' or '',
                    self.serial1.xonxoff and ' Xon/Xoff' or '',))
                self.statusbar.AppendText("\n")
                self.serialconnected = 1

                try:                                     
                    self.basePath = 'C:\\Neurogame\\Subject_' + str(self.systemConfigs.playerID)
                    dirlist = os.listdir(self.basePath)
                    gainfiles = [e for e in dirlist if e.endswith(".pkl")]
                    fnamepath = self.basePath + '\\' + gainfiles[len(gainfiles)-1]  
                    f = file(fnamepath, 'r')
                    self.chA5xGain = pickle.load(f)
                    self.chB5xGain = pickle.load(f)
                    self.chAGain = pickle.load(f)
                    self.chBGain = pickle.load(f)
                    self.chAPGA = pickle.load(f)
                    self.chBPGA = pickle.load(f)
                    self.SetNeurochipGains(self)            
                    time.sleep(1)
                    self.SynchNeurochipGains(self)
                    self.statusbar.AppendText("Neurochip Update Sucessful\n")
                    time.sleep(2)
                    self.DisplayNeurochipGains(self)
                    
                except:
                    try:
                        self.SynchNeurochipGains(self)
                        time.sleep(2)
                        self.DisplayNeurochipGains(self)
                    except:
                        self.statusbar.AppendText("Game Box: Is the power ON and USB cable connected?\n")
                        self.StopThread()
                        self.serial1.close()
                        self.serialconnected = 0
        if self.serialconnected:
            self.calibrateEMG.Enable(True)
            self.connectDevice.Enable(False)
        event.Skip()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def SetNeurochipGains(self, event):
        ChA5x = numpy.add(self.chA5xGain,4)
        ChB5x = numpy.multiply(self.chB5xGain,2)
        Gain5xSend = numpy.add(ChA5x,ChB5x)
        chAGainSend = numpy.add(self.chAGain,99)
        chBGainSend = numpy.add(self.chBGain,199)
        chAPGASend = numpy.add(self.chAPGA,130)
        chBPGASend = numpy.add(self.chBPGA,230)
        self.serial1.write(chr(Gain5xSend))
        self.serial1.write(chr(chAGainSend))
        self.serial1.write(chr(chBGainSend))
        self.serial1.write(chr(chAPGASend))
        self.serial1.write(chr(chBPGASend))
        self.serial1.write(chr(2))
        print "\nGains set sucessfully to Neurochip"

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def DisplayNeurochipGains(self, event):
        if self.chA5xGain == 0:
            ChA5xCheck = 1;
        else:
            ChA5xCheck = 5;
        if self.chB5xGain == 0:
            ChB5xCheck = 1;
        else:
            ChB5xCheck = 5;
 
        # Calculate PGA gains: value refers to the # in list (e.g., entry 2), not actual value shown (e.g., 1.06)
        # 1 is a PGA gain of 1.00 (need to zero pad python array below). Zero is ignored and does not change the current PGA gain.
        PGAGainArray = pyarray.array('d', [0.0,1.00,1.06,1.14,1.23,1.33,1.46,1.60,1.78,2.00,2.27,2.67,3.20,4.00,5.33,8.00,16.0])
        ChATotFGain = numpy.multiply(self.chAGain,ChA5xCheck)
        ChBTotFGain = numpy.multiply(self.chBGain,ChB5xCheck)
        self.ChATotalGain = numpy.multiply(ChATotFGain,PGAGainArray[self.chAPGA])
        self.ChBTotalGain = numpy.multiply(ChBTotFGain,PGAGainArray[self.chBPGA])

        print "Channel A 5x gain = " + str(self.chA5xGain) + ", Filter Gain = " + str(self.chAGain) + ", PGA index = " + str(self.chAPGA)
        print "Channel B 5x gain = " + str(self.chB5xGain) + ", Filter Gain = " + str(self.chBGain) + ", PGA index = " + str(self.chBPGA)
        print "Right Channel A Total Gain = " + str(self.ChATotalGain)
        print "Left Channel B Total Gain = " + str(self.ChBTotalGain)
        self.statusbar.AppendText("Left Gain = " + str(self.ChBTotalGain) + "    Right Gain = " + str(self.ChATotalGain) + "\n")
        self.statusbar.AppendText("Great! Now click the \"Muscle Contraction Test\" button to calibrate your device.\n")

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def SynchNeurochipGains (self, event):
        n = self.serial1.inWaiting()
        junk = self.serial1.read(n)

        self.StopThread()
        time.sleep(0.02)
        self.serial1.write(chr(3))                      # Ping for gains (126 header)
        time.sleep(0.1)
        reading = 1
        serialbuffer = pyarray.array('b')

        while reading:
            text = self.serial1.read(1)
            if text:
                n = self.serial1.inWaiting()
                if n:
                    text = text + self.serial1.read(n)
            serialbuffer.fromstring(text)
            pos = 0
            while pos < n:
                while serialbuffer[pos] != 126:
                    pos += 1
                Gain5xCheck = serialbuffer[pos+1]
                self.chAGain = serialbuffer[pos+2]
                self.chAPGA = serialbuffer[pos+3]
                self.chBGain = serialbuffer[pos+4]
                self.chBPGA = serialbuffer[pos+5]
                pos = n # stop looking for gain information in this packet
            reading = 0 # stop reading buffer

        if Gain5xCheck == 0:
            self.chA5xGain = 0 
            self.chB5xGain = 0  
        elif Gain5xCheck == 1:
            self.chA5xGain = 1 
            self.chB5xGain = 0  
        elif Gain5xCheck == 2:
            self.chA5xGain = 0 
            self.chB5xGain = 1 
        elif Gain5xCheck == 3:
            self.chA5xGain = 1 
            self.chB5xGain = 1
        else:
            print "**Error decoding 5x gain - other gain values suspect**"
            ChA5xCheck = 0
            ChB5xCheck = 0

        self.StartSerialPortThreads()
        print "Gains sucessfully sync'd from Neurochip"

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def ComputerWiringHelp(self, event): 
        steps = ['systemSetup1', 'systemSetup2', 'systemSetup3', 'systemSetup4', 'systemSetup5']
        count = 0
        result1 = wx.ID_OK
        while result1 != wx.ID_EXIT:
            exec('result1 = self.' + steps[count] + '.ShowModal()')
            if result1 == wx.ID_BACKWARD:
                    count = count-1
                    print steps[count]
            elif result1 == wx.ID_FORWARD:
                    count = count+1
                    print steps[count]
        event.Skip()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnButtonTestDongle(self, event): 
        steps = ['userSetup1', 'userSetup2', 'userSetup3', 'userSetup4', 'userSetup5', 'userSetup6', 'userSetup7']
        count = 0
        result1 = wx.ID_OK
        while result1 != wx.ID_EXIT:
            exec('result1 = self.' + steps[count] + '.ShowModal()')
            if result1 == wx.ID_BACKWARD:
                    count = count-1
                    print steps[count]
            elif result1 == wx.ID_FORWARD:
                    count = count+1
                    print steps[count]
        event.Skip()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnTextSelGame(self, event): 
        event.Skip()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnTextEnterSelGame(self, event):
        event.Skip()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnComboBoxSelGame(self, event): 
        event.Skip()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnButtonStartGame(self, event):
        gamestr = self.gameSelection.GetValue()
        config = []
        for game in self.configGames:
            if game.gameName == gamestr:
                config = game
                break
            
        if config:
            if not self.gameSessionHandler.started:
                self.StartGame(config) 
            else:
                self.StopGame() 
        event.Skip()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def StartGame(self, config): 
        self.gameSessionHandler.Start(self.systemConfigs.playerID, config.gameName, self.systemConfigs.gainEMG, self.systemConfigs.slopeEMG, self.systemConfigs.serialSampleRate)
        config.start_game()
        self.currentGameConfig = config
        self.enabledMouseEMG = True 
        
        
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def StopGame(self): 
        self.gameSessionHandler.Stop()
        if self.currentGameConfig:
            self.currentGameConfig.stop_game()
        self.gameSessionHandler.saveDataLocally(self.chA5xGain,self.chAGain,self.chAPGA,self.chB5xGain,self.chBGain,self.chBPGA)
        self.gameSessionHandler.secureServerUpload(self.systemConfigs.playerID, self.systemConfigs.serverHost, self.systemConfigs.serverDir, self.systemConfigs.serverLogin)
        self.currentGameConfig = []
        self.enabledMouseEMG = False

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnButtonDonePlaying(self, event): 
        self.Close()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnMouseMove(self, event):
         return True
    
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnMouseWheel(self, event):
        return True

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnKeyCharEvent(self, event):
        return True

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnKeyDownEvent(self, event):
        if self.keymonitor.update_key_down(event):
            #print "keyID=" + str(self.keymonitor.keyID) + " alt_down=" + str(self.keymonitor.alt_down) 
            
            if self.keymonitor.keyID==123 and self.keymonitor.ctrl_down:            # Control Interface (F12 = 123)
                    self.scopeWindowEMG.Show(True)
                    self.scopeWindowEMG.shown=True
            if self.keymonitor.keyID==123 and self.keymonitor.alt_down:
                    result = self.systemConfigs.ShowModal()
                    if result == wx.ID_OK or event is not None:
                        ok = True
                        self.SaveConfigDefaults()
                    else:
                        ok = False

            if self.keymonitor.keyID==ord('M') and self.keymonitor.alt_down:        # toggle EMG to mouse conversion on/off = alt+M
                self.enabledMouseEMG = not self.enabledMouseEMG
                self.maxEMG = [pyarray.array("f"),pyarray.array("f")]
                self.zcBufEMG = [pyarray.array("f"),pyarray.array("f")]
                self.mouseCenter[0] = self.mousePosition[0]
                self.mouseCenter[1] = self.mousePosition[1]
                self.statusbar.AppendText("EMG -> mouse connection = " + str(self.enabledMouseEMG) + "\n")
                print "EMG2mouse=" + str(self.enabledMouseEMG) 
    
            elif self.keymonitor.keyID==38 and self.keymonitor.alt_down:            # EMG2Mouse conversion gain+ = up arrow (KEYID_ARROW_UP = 38)
                self.systemConfigs.gainEMG +=.1
                self.convertInputTranslation.SetParams(self.systemConfigs.gainEMG, self.systemConfigs.slopeEMG, self.systemConfigs.EMGxoffset, 256)
                self.statusbar.AppendText("EMG conv gain = " + str(self.systemConfigs.gainEMG) + "\n")
 
            elif self.keymonitor.keyID==40 and self.keymonitor.alt_down:            # EMG2Mouse conversion gain- = down arrow (KEYID_ARROW_DOWN = 40)
                self.systemConfigs.gainEMG -= max(0,self.systemConfigs.gainEMG-.1)
                self.convertInputTranslation.SetParams(self.systemConfigs.gainEMG, self.systemConfigs.slopeEMG, self.systemConfigs.EMGxoffset, 256)
                self.statusbar.AppendText("EMG conv gain = " + str(self.systemConfigs.gainEMG) + "\n")

            elif self.keymonitor.keyID==33 and self.keymonitor.alt_down:            # EMG2Mouse conversion slope+ = pgdn (KEYID_PAGE_UP = 33)
                self.systemConfigs.slopeEMG += .002
                self.convertInputTranslation.SetParams(self.systemConfigs.gainEMG, self.systemConfigs.slopeEMG, self.systemConfigs.EMGxoffset, 256)
                self.statusbar.AppendText("EMG conv slope = " + str(self.systemConfigs.slopeEMG) + "\n")
            
            elif self.keymonitor.keyID==34 and self.keymonitor.alt_down:            # EMG2Mouse conversion slope- = pgdn (KEYID_PAGE_DOWN = 34)
                self.systemConfigs.slopeEMG -= .002
                self.convertInputTranslation.SetParams(self.systemConfigs.gainEMG, self.systemConfigs.slopeEMG, self.systemConfigs.EMGxoffset, 256)
                self.statusbar.AppendText("EMG conv slope = " + str(self.systemConfigs.slopeEMG) + "\n")

            elif self.keymonitor.keyID==37 and self.keymonitor.alt_down:            # EMG2Mouse conversion x offset- = alt+left arrow (KEYID_ARROW_LEFT = 37)
                self.systemConfigs.EMGxoffset = max(-128,self.systemConfigs.EMGxoffset-5) 
                self.convertInputTranslation.SetParams(self.systemConfigs.gainEMG, self.systemConfigs.slopeEMG, self.systemConfigs.EMGxoffset, 256)
                self.statusbar.AppendText("EMG conv offset = " + str(self.systemConfigs.EMGxoffset) + "\n")

            elif self.keymonitor.keyID==39 and self.keymonitor.alt_down:    # EMG2Mouse conversion x offset+ = alt+right arrow (KEYID_ARROW_RIGHT = 39)
                self.systemConfigs.EMGxoffset += 5
                self.convertInputTranslation.SetParams(self.systemConfigs.gainEMG, self.systemConfigs.slopeEMG, self.systemConfigs.EMGxoffset, 256)
                self.statusbar.AppendText("EMG conv offset = " + str(self.systemConfigs.EMGxoffset) + "\n")
            
            elif self.keymonitor.keyID==112:    # F1 = Left Neurochip EMG Gain -- Large increment (KEYID_PAGE_F1 = 112)
                gain_adjust = self.AdjustNeurochipGains(self.chB5xGain,self.chBGain,self.chBPGA,-1,1)
                self.chB5xGain = gain_adjust[0]
                self.chBGain = gain_adjust[1]                            
                self.chBPGA = gain_adjust[2]
                self.SetNeurochipGains(self)
                self.DisplayNeurochipGains(self)
            
            elif self.keymonitor.keyID==113:    # F2 = Left Neurochip EMG Gain - small increment (KEYID_PAGE_F2 = 113)
                gain_adjust = self.AdjustNeurochipGains(self.chB5xGain,self.chBGain,self.chBPGA,-1,0)
                self.chB5xGain = gain_adjust[0]
                self.chBGain = gain_adjust[1]                            
                self.chBPGA = gain_adjust[2]             
                self.SetNeurochipGains(self)
                self.DisplayNeurochipGains(self)
            
            elif self.keymonitor.keyID==114:    # F3 = Left Neurochip EMG Gain + small increment (KEYID_PAGE_F3 = 114)
                gain_adjust = self.AdjustNeurochipGains(self.chB5xGain,self.chBGain,self.chBPGA,1,0)
                self.chB5xGain = gain_adjust[0]
                self.chBGain = gain_adjust[1]                            
                self.chBPGA = gain_adjust[2]             
                self.SetNeurochipGains(self)
                self.DisplayNeurochipGains(self)

            elif self.keymonitor.keyID==115:    # F3 = Left Neurochip EMG Gain ++ large increment(KEYID_PAGE_F4 = 115)
                gain_adjust = self.AdjustNeurochipGains(self.chB5xGain,self.chBGain,self.chBPGA,1,1)
                self.chB5xGain = gain_adjust[0]
                self.chBGain = gain_adjust[1]                            
                self.chBPGA = gain_adjust[2]
                self.SetNeurochipGains(self)
                self.DisplayNeurochipGains(self)

            elif self.keymonitor.keyID==116:    # F5 = Right Neurochip EMG gain -- large increment (KEYID_PAGE_F5 = 116)
                gain_adjust = self.AdjustNeurochipGains(self.chA5xGain,self.chAGain,self.chAPGA,-1,1)
                self.chA5xGain = gain_adjust[0]
                self.chAGain = gain_adjust[1]                            
                self.chAPGA = gain_adjust[2]
                self.SetNeurochipGains(self)
                self.DisplayNeurochipGains(self)

            elif self.keymonitor.keyID==117:    # F6 = Right Neurochip EMG gain - small increment(KEYID_PAGE_F2 = 117)
                gain_adjust = self.AdjustNeurochipGains(self.chA5xGain,self.chAGain,self.chAPGA,-1,0)
                self.chA5xGain = gain_adjust[0]
                self.chAGain = gain_adjust[1]                            
                self.chAPGA = gain_adjust[2]
                self.SetNeurochipGains(self)
                self.DisplayNeurochipGains(self)

            elif self.keymonitor.keyID==118:    # F7 = Right Neurochip EMG Gain + smallest step (KEYID_PAGE_F7 = 118)
                gain_adjust = self.AdjustNeurochipGains(self.chA5xGain,self.chAGain,self.chAPGA,1,0)
                self.chA5xGain = gain_adjust[0]
                self.chAGain = gain_adjust[1]                            
                self.chAPGA = gain_adjust[2]
                self.SetNeurochipGains(self)
                self.DisplayNeurochipGains(self)

            elif self.keymonitor.keyID==119:   #  F8 = Right Neurochip EMG Gain ++ large step (KEYID_PAGE_F8 = 119)          
                gain_adjust = self.AdjustNeurochipGains(self.chA5xGain,self.chAGain,self.chAPGA,1,1)
                self.chA5xGain = gain_adjust[0]
                self.chAGain = gain_adjust[1]                            
                self.chAPGA = gain_adjust[2]
                self.SetNeurochipGains(self)
                self.DisplayNeurochipGains(self)

            elif self.keymonitor.keyID==122 and self.keymonitor.alt_down:       # F11 = Right Neurochip EMG Gain - (F9 = 122)
                if self.ChATotalGain < 5.0:
                    while self.ChATotalGain < 5.0:
                        gain_adjust = self.AdjustNeurochipGains(self.chA5xGain,self.chAGain,self.chAPGA,1,1)
                        self.chA5xGain = gain_adjust[0]
                        self.chAGain = gain_adjust[1]                            
                        self.chAPGA = gain_adjust[2]
                        self.SetNeurochipGains(self)
                        self.DisplayNeurochipGains(self)
                elif self.ChATotalGain > 5.0:
                    while self.ChATotalGain > 5.0:
                        gain_adjust = self.AdjustNeurochipGains(self.chA5xGain,self.chAGain,self.chAPGA,-1,1)
                        self.chA5xGain = gain_adjust[0]
                        self.chAGain = gain_adjust[1]                            
                        self.chAPGA = gain_adjust[2]
                        self.SetNeurochipGains(self)
                        self.DisplayNeurochipGains(self)
                if self.ChBTotalGain < 5.0:
                    while self.ChBTotalGain < 5.0:
                        gain_adjust = self.AdjustNeurochipGains(self.chB5xGain,self.chBGain,self.chBPGA,1,1)
                        self.chB5xGain = gain_adjust[0]
                        self.chBGain = gain_adjust[1]                            
                        self.chBPGA = gain_adjust[2]
                        self.SetNeurochipGains(self)
                        self.DisplayNeurochipGains(self)
                elif self.ChBTotalGain > 5.0:
                    while self.ChBTotalGain > 5.0:
                        gain_adjust = self.AdjustNeurochipGains(self.chB5xGain,self.chBGain,self.chBPGA,-1,1)
                        self.chB5xGain = gain_adjust[0]
                        self.chBGain = gain_adjust[1]                            
                        self.chBPGA = gain_adjust[2]
                        self.SetNeurochipGains(self)
                        self.DisplayNeurochipGains(self)
 
            elif self.keymonitor.keyID==ord('X') and self.keymonitor.alt_down:
                self.OnExit(event)
            elif self.keymonitor.keyID==37:
                self.lastValueEMG -= 2
            elif self.keymonitor.keyID==39:
                self.lastValueEMG += 2
        return True

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def AdjustNeurochipGains(self,x5,Filt,PGA,direction,full_step):
        if x5 ==0:                  # Define 5x gains off (0) or on (1) here 
            x5Check = 1
        else:
            x5Check = 5

        # PGA lookup array (values in PGA refer to 1-based index in list)
        PGAGainArray = pyarray.array('d', [0.0,1.00,1.06,1.14,1.23,1.33,1.46,1.60,1.78,2.00,2.27,2.67,3.20,4.00,5.33,8.00,16.0])
        TotFGain = numpy.multiply(Filt,x5Check)           
        OrigTotalGain = numpy.multiply(TotFGain,PGAGainArray[PGA])
        
        if direction == 1:                      # increase gain 
            if full_step:                       # By large steps in filt, then filt x5
                Filt +=1
                PGA = 1
                if Filt > 9 and x5 == 0:        # if this bump will take the filter gain to 10, implement 5x gain
                    Filt = 2
                    x5 = 1  
            else:                               # by smallest increment
                bumpPGA = numpy.multiply(numpy.multiply(Filt,x5Check),PGAGainArray[PGA+1])
                bumpfilt = numpy.multiply(PGAGainArray[1],numpy.multiply(Filt+1,x5Check))
                if (bumpPGA-OrigTotalGain) < (bumpfilt-OrigTotalGain):
                    PGA +=1
                else:
                    Filt +=1
                    PGA = 1
                    if Filt > 9 and x5 == 0:    # if this bump will take the filter gain to 10, implement 5x gain
                        Filt = 2
                        x5 = 1              
        elif direction == -1:                   # decrease gains 
            if full_step:                       # by large step
                Filt -=1
                PGA = 1
                if Filt < 3 and x5 == 1:        # if this bump will take the filter gain below 3, turn off 5x gain
                    Filt = 10
                    x5 = 0
                    x5Check = 1
            else:                               # by smallest increment
                if PGA != 1:
                    bumpPGA = numpy.multiply(numpy.multiply(Filt,x5Check),PGAGainArray[PGA-1])
                    bumpfilt = numpy.multiply(PGAGainArray[PGA],numpy.multiply(Filt-1,x5Check))
                    if (OrigTotalGain-bumpPGA) < (OrigTotalGain-bumpfilt):
                        PGA -=1 
                else:
                    Filt -=1
                    if Filt < 3 and x5 == 1:    # if this bump will take the filter gain below 3, turn off 5x gain
                        Filt = 10
                        x5 = 0
                        x5Check = 1
                    PGAindex = 8        # find largest PGA gain that results in decrease from orig, count down from 8th value (1.78)
                    PGAtestgain = numpy.multiply(PGAGainArray[PGAindex],numpy.multiply(Filt,x5Check))
                    while PGAtestgain > OrigTotalGain:
                        PGAindex -=1
                        PGAtestgain = numpy.multiply(PGAGainArray[PGAindex],numpy.multiply(Filt,x5Check))
                    PGA = PGAindex
            NewTotalGain = numpy.multiply(numpy.multiply(Filt,x5Check),PGAGainArray[PGA])       # Check that gain not less than 1
            if NewTotalGain < 1:
                Filt = 1
                PGA = 1
        return [x5,Filt,PGA]

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnCalibrateEMG(self, event):
        # The following happens if you click the "Muscle Contraction Test" button while the MVC routine is running
        if self.scopeWindowMVC.shown:
            print "Aborting MVC Tests via Muscle Contraction Test Click"
            self.scopeWindowMVC.shown=False
            self.scopeWindowMVC.Show(False)
            self.scopeWindowMVC.Close()
            self.collectMVC.Stop()
            self.MVCBaselineInProgress = False
            self.MVCRelaxInProgress = False
            self.MVCCollectionInProgress = False
            self.MVCTestInProgress = False         
            self.calibrateEMG.Enable(True)
            self.selectGameText.Enable(True)
            self.gameSelection.Enable(True)
            self.beginGameplay.Enable(True)
            self.finishGameplay.Enable(True)
            return

        # Run MVC tests as normal:
        self.collectMVC.Start(self.systemConfigs.playerID, self.systemConfigs.gainEMG, self.systemConfigs.slopeEMG, self.systemConfigs.serialSampleRate)
        self.scopeWindowMVC.Show(True)
        self.scopeWindowMVC.shown=True
        
        # Create empty MVC buffer for processing and storing MVC data
        #self.MVCbuffer = [pyarray.array('B'), pyarray.array('B')]
        #self.MVCSmoothing = 300 # number of samples at 1000 Hz to average rectified MVC value before displaying
        #self.MVCframe = 0 # counting for EMG smoothing update
        #self.MVCLastUpdate = 0
        self.smoothMVCData = [pyarray.array('f')]
        self.MVCmax = [pyarray.array('f'),pyarray.array('f')]
        self.MVCmin = [pyarray.array('f'),pyarray.array('f')]
        self.MVCbaseline = [pyarray.array('f'),pyarray.array('f')]

        # Text cues for muscles 0 (right) and 1 (left) movement
        self.muscleText = [pyarray.array('c'),pyarray.array('c')]     
        self.muscleText[0] = self.systemConfigs.rightward
        self.muscleText[1] = self.systemConfigs.leftward
        self.numMVCs = 3                            # Define number of MVCs
        self.numMVCsRemain = 3

        # Time to spend in each period (s)
        self.BaselineTime = 6 
        self.CountdownTime = 3
        self.RelaxCountdown = 4
        self.MVCTime = 4
        self.MVCymax = 60
        self.new_MVCymax = self.MVCymax 
        self.MVCchan = int(0)  
        print "MVC Tests Beginning" 

        # Begin baseline collection period period
        self.MVCBaselineInProgress = True
        self.MVCRelaxInProgress = False
        self.MVCBaselineTime = self.BaselineTime
        self.BaselineStart = time.clock()
        self.scopeWindowMVC.add_data([0,0], 0)
        self.scopeWindowMVC.config_plot(0,self.MVCymax)      
        return True
        
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnKeyUpEvent(self, event):
        self.keymonitor.update_key_up(event)
        return True

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnClose(self, event):
        self.timer.Stop()
        self.StopThread()   
        self.StopWiiThread()                        
        self.serial1.close()   
        self.wiimote.shut_down_wiimote()                     
        self.reminderImagesEnd.ShowModal()
        self.Destroy()                              
        self.dialogSerialConfig.Destroy()
        self.scopeWindowEMG.Destroy()
        self.scopeWindowMVC.Destroy()
        self.reminderImages.Destroy()
        self.systemConfigs.Destroy()
        self.reminderImagesEnd.Destroy()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnChar(self, event):
        event.Skip()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def StartSerialPortThreads(self):
        self.thread1 = threading.Thread(target=self.ComPortThread1)
        self.thread1.setDaemon(1)
        self.alive1.set()
        self.thread1.start()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def StartWiimoteInput(self):
        self.thread2 = threading.Thread(target=self.WiimotePolling)
        self.thread2.setDaemon(1)
        self.alive2.set()
        self.thread2.start()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def StopThread(self):
        if self.thread1 is not None:
            self.alive1.clear()          # clear alive event for thread
            self.thread1.join()          # wait until thread has finished
            self.thread1 = None

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def StopWiiThread(self):
        if self.thread2 is not None:
            self.alive2.clear()          #clear alive event for thread
            self.thread2.join()          #wait until thread has finished
            self.thread2 = None
                    
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnSerialRead(self, event):
        """Handle input from the serial port."""
  
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def OnTimerUpdate(self, event):
        updated = False

        if len(self.serialbuffer) > 0:
            self.ProcessSerialData() # process serial data to the channel buffers
            updated = True
            
        if self.enabledMouseEMG and self.simEMG: 
            curspos = self.calcMouseMovement()
            self.mouseHidden[0] += numpy.sign(curspos[0]) 
            self.mouseHidden[1] += numpy.sign(curspos[1])
            userEvent.m_move(int(round(self.mouseHidden[0])), int(round(self.mouseHidden[1])))

        elif updated:
            self.lastValueEMG, curspos, tdif = self.calcMouseMovement(self.lastValueEMG)
            if self.enabledMouseEMG:
                userEvent.m_scroll(int(tdif*200))
                #print "OnTimerUpdate, if self.enabledMouseEMG"
                #amtMoved = int(tdif*200)
                #self.totalAmtMoved = self.totalAmtMoved + amtMoved
                #if self.totalAmtMoved > 144000:
                #    skip_amount = int(-200000)
                #    print skip_amount
                #    userEvent.m_scroll_reset(skip_amount)
                #    self.totalAmtMoved = 0
                #else:
                #    #userEvent.m_scroll(int(tdif*200))
                #    userEvent.m_scroll(amtMoved)
                
            if self.mouseTest:
                self.test_slider.SetValue(curspos[0])

            if self.CheckSerialStream:
                ratioA = numpy.divide(self.fifobuffer100a.mean(),self.fifobuffer100a.median())
                ratioB = numpy.divide(self.fifobuffer100b.mean(),self.fifobuffer100b.median())
                if abs(ratioA) > 2: # could also look at less than 0.5, or channel B if not noisy
                    print "High ratio of mean/median on channel A: Serial glitch?"
                    self.Reset_Serial_Port()

            # MVC baseline collection period, this should only occur twice -- once before left movement, once before right
            if self.MVCBaselineInProgress:
                # Get the average of the 300 sample FIFO Buffer for the active channel (filled in serial ProcessSerialData)
                feedback_level = self.fifobuffer300.mean()  # try median for smoother display, or try moving to timer update?
                self.smoothMVCData.append(feedback_level)   # Add the smoothed data to the buffer for calculating max/min at end of attempt
                
                # If the baseline monitoring time = 0, switch to collection time
                if self.MVCBaselineTime == 0:               
                    print "Switch from Baseline Collection to MVC Countdown (means MVCBaselineTime == 0)"
                    self.MVCBaselineInProgress = False
                    self.MVCCollectionInProgress = True
                    self.MVCCountdownTime = self.CountdownTime
                    self.MVCbaseline[self.MVCchan].append(min(self.smoothMVCData[1 :]))             # Calculate min of baseline period using smoothed buffer
                    self.smoothMVCData = [pyarray.array('f')]                                       # Flush buffer              
                
                # Pre-flex-collection countdown (baseline collection) period                        
                if time.clock() - self.BaselineStart >= 1:  # if num of seconds elapsed since first call - number of seconds elapsed since? whaa?
                    self.BaselineStart = time.clock()
                    self.MVCBaselineTime -= 1                                   # Counter (in "3.. 2.. 1") for the message text
                    self.scopeWindowMVC.instructions.SetLabel("Relax...")
                    self.scopeWindowMVC.instructions2.SetLabel("In " + str(self.MVCBaselineTime) + " seconds, bend your wrist to the " + self.muscleText[self.MVCchan] + ".")
                    self.scopeWindowMVC.instructions2.Wrap(400)               # Wraps text to the window size
                    self.scopeWindowMVC.relax_time(0)                         # Sets the color-meter graph to grey
            
            # Collect actual flex data
            if self.MVCCollectionInProgress:
                # This occurs if the statement below is false, and the countdown has reached 0
                self.MVCCollectionInProgress = False             
                self.MVCTestInProgress = True
                self.MVCRelaxCountdown = self.RelaxCountdown
                self.MVCCountdownStart = time.clock()
                self.scopeWindowMVC.instructions.SetLabel("Flex!")
                self.scopeWindowMVC.instructions2.SetLabel("Begin! Bend your wrist to the " + self.muscleText[self.MVCchan]  + ", as far as possible!") # + str(self.MVCCountdownTime) + " seconds", size=12)
                print "Begin! Bend your wrist to the " + self.muscleText[self.MVCchan]  + ", as far as possible!\n"
                self.scopeWindowMVC.instructions2.Wrap(400)
                self.scopeWindowMVC.draw_channel(0)                   
                    
            # Update the MVC display and store data in the smoothed buffer
            if self.MVCTestInProgress: 
                # Get the average of the 300 sample FIFO Buffer for the active channel (filled in serial ProcessSerialData)
                feedback_level = self.fifobuffer300.mean() # try median for smoother display, or try moving to timer update?
                # add the active MVC channel's smoothed data to the MVC scope window and draw/clear
                self.scopeWindowMVC.add_data([feedback_level,feedback_level], 0)               
                self.scopeWindowMVC.draw_channel(0)
                self.scopeWindowMVC.clear_channel(0)
                self.smoothMVCData.append(feedback_level)                           # Add the smoothed data to the buffer for calculating max/min
                
                if self.MVCCountdownTime == 0:                                      # Summarize data and move to the next test period
                    self.numMVCsRemain -= 1
                    self.MVCTestInProgress = False 

                    # Calculate max of MVC period using smoothed buffer and store data in array for later saving 
                    self.MVCmax[self.MVCchan].append(max(self.smoothMVCData[1 :]))
                    self.MVCmin[self.MVCchan].append(min(self.smoothMVCData[1 :]))

                    if max(self.smoothMVCData[1 :])> max(self.MVCymax,self.new_MVCymax):    # Adjust MVC screen resolution
                        self.new_MVCymax = numpy.multiply(max(self.smoothMVCData[1 :]),1.2)
                        self.scopeWindowMVC.config_plot(0,self.new_MVCymax)         # Starts with default of 60 units in y-axis
                    self.smoothMVCData = [pyarray.array('f')]                       # Flush buffer
                    self.MVCRelaxInProgress = True
                    self.relaxStart = time.clock()

                elif time.clock() - self.MVCCountdownStart >= 1: # update the countdown timer
                    self.MVCCountdownStart = time.clock()
                    self.MVCCountdownTime -= 1

            if self.MVCRelaxInProgress:                             # Display relax for N seconds, then move on         
                if time.clock() - self.relaxStart >= 1:
                    self.relaxStart = time.clock()
                    self.MVCRelaxCountdown -= 1
                    self.scopeWindowMVC.instructions.SetLabel("Relax...")
                    self.scopeWindowMVC.instructions2.SetLabel("Great! Now relax your arm completely for " + str(self.MVCRelaxCountdown) + " seconds.")
                    self.scopeWindowMVC.instructions2.Wrap(400)
                    self.scopeWindowMVC.relax_time(0)                 # Sets the color-meter graph to grey

                if self.MVCRelaxCountdown == 0:
                    self.MVCRelaxInProgress = False        
                    if self.numMVCsRemain != 0:
                        self.MVCCollectionInProgress = True
                        self.MVCCountdownTime = self.CountdownTime
                    elif self.numMVCsRemain == 0 and self.MVCchan == 0:
                        self.numMVCsRemain = self.numMVCs 
                        self.MVCchan = 1
                        self.MVCBaselineInProgress = True
                        self.MVCBaselineTime = self.BaselineTime
                        self.BaselineStart = time.clock()
                        self.scopeWindowMVC.config_plot(0,self.MVCymax) 
                        self.new_MVCymax = self.MVCymax
                    elif self.numMVCsRemain == 0 and self.MVCchan == 1:
                        self.scopeWindowMVC.shown=False
                        self.scopeWindowMVC.Show(False)
                        self.scopeWindowMVC.Close()

                        # Save max and baseline MVC data to file at end of run (i.e., send values to text or pickle file)
                        print "Max MVCs Right: " + str(self.MVCmax[0]) + "    Left: " + str(self.MVCmax[1])
                        print "Min MVCs Left: " + str(self.MVCmin[0]) + "   Left: " + str(self.MVCmin[1])
                        print "Baselines Right: " + str(self.MVCbaseline[0]) + "   Left: " + str(self.MVCbaseline[1])
                        self.diffChAMVC = [self.MVCmax[0][0] - self.MVCbaseline[0][0], self.MVCmax[0][1] - self.MVCbaseline[0][0], self.MVCmax[0][2] - self.MVCbaseline[0][0]]
                        self.diffChBMVC = [self.MVCmax[1][0] - self.MVCbaseline[1][0], self.MVCmax[1][0] - self.MVCbaseline[1][0], self.MVCmax[1][2] - self.MVCbaseline[1][0]]
                        self.avgDiffChAMVC = sum(self.diffChAMVC) / float(len(self.diffChAMVC))
                        self.avgDiffChBMVC = sum(self.diffChBMVC) / float(len(self.diffChBMVC))

                        if self.avgDiffChAMVC > 40:
                            self.optimalGainChA = 1
                        elif self.avgDiffChAMVC > 37.5:
                            self.optimalGainChA = 1.5
                        elif self.avgDiffChAMVC > 35:
                            self.optimalGainChA = 2
                        elif self.avgDiffChAMVC > 32.5:
                            self.optimalGainChA = 2.5
                        elif self.avgDiffChAMVC > 30:
                            self.optimalGainChA = 3
                        elif self.avgDiffChAMVC > 27.5:
                            self.optimalGainChA = 4
                        elif self.avgDiffChAMVC > 25:
                            self.optimalGainChA = 5
                        elif self.avgDiffChAMVC > 22.5:
                            self.optimalGainChA = 6
                        elif self.avgDiffChAMVC > 20:
                            self.optimalGainChA = 7
                        elif self.avgDiffChAMVC > 17.5:
                            self.optimalGainChA = 8
                        elif self.avgDiffChAMVC > 15:
                            self.optimalGainChA = 9
                        elif self.avgDiffChAMVC > 12.5:
                            self.optimalGainChA = 10
                        elif self.avgDiffChAMVC > 10:
                            self.optimalGainChA = 11
                        elif self.avgDiffChAMVC > 7.5:
                            self.optimalGainChA = 12
                        elif self.avgDiffChAMVC > 5:
                            self.optimalGainChA = 13
                        elif self.avgDiffChAMVC > 2.5:
                            self.optimalGainChA = 14
                        elif self.avgDiffChAMVC > 1:
                            self.optimalGainChA = 15
                        else:
                            self.optimalGainChA = 19

                        if self.avgDiffChBMVC > 40:
                            self.optimalGainChB = 1
                        elif self.avgDiffChBMVC > 37.5:
                            self.optimalGainChB = 1.5
                        elif self.avgDiffChBMVC > 35:
                            self.optimalGainChB = 2
                        elif self.avgDiffChBMVC > 32.5:
                            self.optimalGainChB = 2.5
                        elif self.avgDiffChBMVC > 30:
                            self.optimalGainChB = 3
                        elif self.avgDiffChBMVC > 27.5:
                            self.optimalGainChB = 4
                        elif self.avgDiffChBMVC > 25:
                            self.optimalGainChB = 5
                        elif self.avgDiffChBMVC > 22.5:
                            self.optimalGainChB = 6
                        elif self.avgDiffChBMVC > 20:
                            self.optimalGainChB = 7
                        elif self.avgDiffChBMVC > 17.5:
                            self.optimalGainChB = 8
                        elif self.avgDiffChBMVC > 15:
                            self.optimalGainChB = 9
                        elif self.avgDiffChBMVC > 12.5:
                            self.optimalGainChB = 10
                        elif self.avgDiffChBMVC > 10:
                            self.optimalGainChB = 11
                        elif self.avgDiffChBMVC > 7.5:
                            self.optimalGainChB = 12
                        elif self.avgDiffChBMVC > 5:
                            self.optimalGainChB = 13
                        elif self.avgDiffChBMVC > 2.5:
                            self.optimalGainChB = 14
                        elif self.avgDiffChBMVC > 1:
                            self.optimalGainChB = 15
                        else:
                            self.optimalGainChB = 19

                        print "self.optimalGainChA: " + str(self.optimalGainChA)
                        print "self.optimalGainChB: " + str(self.optimalGainChB)

                        if self.ChATotalGain < self.optimalGainChA:
                            while self.ChATotalGain < self.optimalGainChA:
                                gain_adjust = self.AdjustNeurochipGains(self.chA5xGain,self.chAGain,self.chAPGA,1,1)
                                self.chA5xGain = gain_adjust[0]
                                self.chAGain = gain_adjust[1]                            
                                self.chAPGA = gain_adjust[2]
                                self.SetNeurochipGains(self)                # Call function to set new gains to Neurochip
                                self.DisplayNeurochipGains(self)
                        elif self.ChATotalGain > self.optimalGainChA:
                            while self.ChATotalGain > self.optimalGainChA:
                                gain_adjust = self.AdjustNeurochipGains(self.chA5xGain,self.chAGain,self.chAPGA,-1,1)
                                self.chA5xGain = gain_adjust[0]
                                self.chAGain = gain_adjust[1]                            
                                self.chAPGA = gain_adjust[2]
                                self.SetNeurochipGains(self)                # Call function to set new gains to Neurochip
                                self.DisplayNeurochipGains(self)

                        if self.ChBTotalGain < self.optimalGainChB:
                            while self.ChBTotalGain < self.optimalGainChB:
                                gain_adjust = self.AdjustNeurochipGains(self.chB5xGain,self.chBGain,self.chBPGA,1,1)
                                self.chB5xGain = gain_adjust[0]
                                self.chBGain = gain_adjust[1]                            
                                self.chBPGA = gain_adjust[2]
                                self.SetNeurochipGains(self)                # Call function to set new gains to Neurochip
                                self.DisplayNeurochipGains(self)
                        elif self.ChBTotalGain > self.optimalGainChB:
                            while self.ChBTotalGain > self.optimalGainChB:
                                gain_adjust = self.AdjustNeurochipGains(self.chB5xGain,self.chBGain,self.chBPGA,-1,1)
                                self.chB5xGain = gain_adjust[0]
                                self.chBGain = gain_adjust[1]                            
                                self.chBPGA = gain_adjust[2]
                                self.SetNeurochipGains(self)                # Call function to set new gains to Neurochip
                                self.DisplayNeurochipGains(self)

                        self.collectMVC.Stop()
                        self.collectMVC.saveDataLocally(self.MVCmax,self.MVCbaseline,self.chA5xGain,self.chAGain,self.chAPGA,self.chB5xGain,self.chBGain,self.chBPGA)
                        self.calibrateEMG.Enable(True)
                        self.selectGameText.Enable(True)
                        self.gameSelection.Enable(True)
                        self.beginGameplay.Enable(True)
                        self.finishGameplay.Enable(True)
                
            if self.EMGCalibrationInProgress:
                if self.mouseMethod > 0:                        # use max envelope
                    self.EMGCalibrationValues[0].append(self.maxEMG[0][-1])
                    self.EMGCalibrationValues[1].append(self.maxEMG[1][-1])
                else:                                           # use zero crossings
                    self.EMGCalibrationValues[0].append(self.zcBufEMG[0][-1])
                    self.EMGCalibrationValues[1].append(self.zcBufEMG[1][-1])

            if self.autocalOnEMG:                              # automatic recalibration
                if self.autocalCountEMG > self.autocalCountEMGThresh:
                    self.systemConfigs.chanoffset[0] = numpy.median(self.EMGCalibrationValues[0])
                    self.systemConfigs.chanoffset[1] = numpy.median(self.EMGCalibrationValues[1])
                    self.EMGCalibrationValues = [pyarray.array("f"), pyarray.array("f")]
                    self.autocalCountEMG = 0
                else:                                           # add latest EMG max to the recal buffer
                    if self.mouseMethod > 0:
                        self.EMGCalibrationValues[0].append(self.maxEMG[0][-1])
                        self.EMGCalibrationValues[1].append(self.maxEMG[1][-1])
                    else:
                        self.EMGCalibrationValues[0].append(self.zcBufEMG[0][-1])
                        self.EMGCalibrationValues[1].append(self.zcBufEMG[1][-1])
                    self.autocalCountEMG += 1
                self.EMGbuffer2 = [pyarray.array('B'), pyarray.array('B')]

        if self.gameSessionHandler.started:                               # check whether the game has exited
            if self.currentGameConfig.game_duration() > 10:
                if not self.currentGameConfig.game_is_running():
                    print "Game window was closed"
                    self.StopGame()
        event.Skip()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def ProcessSerialData(self):
        done = False;
        buflen = len(self.serialbuffer)
        pos = 0
        numframes = 0
        while not done:
            while pos < buflen and self.serialbuffer[pos] != 125:
                pos += 1
            if pos > buflen-20 or self.serialbuffer[pos] != 125:
                done = True
            elif max(self.serialbuffer[pos+1:pos+20]) >= 125: 
                print "Irregular header byte, system serial buffer overrun?"
                self.Reset_Serial_Port()
                done = True
                return
            else: 
                for i in range(0, 9):
                    self.EMGbuffer[0].append(self.serialbuffer[pos+i*2+1]+120)
                    self.EMGbuffer[1].append(self.serialbuffer[pos+i*2+2]+120)
                numframes += 1
                pos += 21

                if pos < buflen:                                        # if there is still more to read
                    if self.serialbuffer[pos] != 125:                   # check that next byte is indeed a header byte
                        print "Next header missing byte where expected, system serial buffer overrun?"
                        self.Reset_Serial_Port()
                        done = True
                        return
            
        if numframes > 0:                                               # truncate front of serial buffer by the number of whole frames received
            self.serialbuffer = self.serialbuffer[numframes*21 : ]
        self.EMGbuffer2[0] += self.EMGbuffer[0]                         # append to second channel buffer, used for processing
        self.EMGbuffer2[1] += self.EMGbuffer[1] 
        if self.scopeWindowMVC.shown:                                   # append EMG data to buffer, used for smoothing/displaying during MVC scope feedback
            diffbuff_Display = diff(self.EMGbuffer[self.MVCchan],1)     # fill the 300 sample FIFO buffer with rectified EMG from the active channel
            for x in range(len(diffbuff_Display)):
                self.fifobuffer300.put(abs(diffbuff_Display[x]))  
        if len(self.EMGbuffer[0]) >= self.systemConfigs.EMGnumSamples:
            if self.gameSessionHandler.started:
                self.gameSessionHandler.Append_EMG_Bytearray(self.EMGbuffer[0], 0)
                self.gameSessionHandler.Append_EMG_Bytearray(self.EMGbuffer[1], 1)
            if self.collectMVC.started:
                self.collectMVC.Append_EMG_Bytearray(self.EMGbuffer[0], 0)
                self.collectMVC.Append_EMG_Bytearray(self.EMGbuffer[1], 1)
            if self.scopeWindowEMG.shown:
                self.scopeWindowEMG.add_data(self.EMGbuffer[0], 0)
                self.scopeWindowEMG.add_data(self.EMGbuffer[1], 1) 
            if self.scopeWindowEMG.shown and len(self.scopeWindowEMG.data[0])>=self.scopeWindowEMG.width():
                self.scopeWindowEMG.draw_channel(0)
                self.scopeWindowEMG.clear_channel(0)
                self.scopeWindowEMG.draw_channel(1)
                self.scopeWindowEMG.clear_channel(1)
            diffbuf = diff(self.EMGbuffer[0],1)
            self.maxEMG[0].append(max(abs(diffbuf)))
            self.zcBufEMG[0].append(self.GetNumZeroCrossings(diffbuf*self.systemConfigs.changain[0], self.systemConfigs.EMGxoffset))
            diffbuf = diff(self.EMGbuffer[1],1)
            self.maxEMG[1].append(max(abs(diffbuf)))
            self.zcBufEMG[1].append(self.GetNumZeroCrossings(diffbuf*self.systemConfigs.changain[1], self.systemConfigs.EMGxoffset))
            if self.CheckSerialStream:
                for x in range (len(self.EMGbuffer[1])):
                    self.fifobuffer100a.put(self.EMGbuffer[1][x])
            self.EMGbuffer[0] = pyarray.array('B')
            self.EMGbuffer[1] = pyarray.array('B')

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def calcMouseMovement(self, lastvalue):
        movement = [0.0, 0.0]
        tdif = None
        
        if self.mouseMethod > 0:          # use max envelope
            chan1val = numpy.median(self.maxEMG[0][-min(int(self.systemConfigs.smoothernummeds),len(self.maxEMG[0])):-1])
            chan2val = numpy.median(self.maxEMG[1][-min(int(self.systemConfigs.smoothernummeds),len(self.maxEMG[1])):-1])
            chan1val = max(0,(chan1val-self.systemConfigs.chanoffset[0])*self.systemConfigs.changain[0])
            chan2val = max(0,(chan2val-self.systemConfigs.chanoffset[1])*self.systemConfigs.changain[1]) 
            xval = self.convertInputTranslation.Convert(int(chan1val), int(chan2val));
            if math.isnan(xval): xval = 0
        else:
            chan1val = numpy.median(self.zcBufEMG[0][-min(int(self.systemConfigs.smoothernummeds),len(self.zcBufEMG[0])):-1])
            chan2val = numpy.median(self.zcBufEMG[1][-min(int(self.systemConfigs.smoothernummeds),len(self.zcBufEMG[1])):-1])
            tdif = chan1val - chan2val
            if math.isnan(tdif): tdif = 0
            xval = tdif*self.systemConfigs.gainEMG 

            if self.systemConfigs.slopeEMG <> 1:
                signx = numpy.sign(xval)
                xval = math.pow(xval*signx,self.systemConfigs.slopeEMG)
                xval *= signx                 
        movement[1] = 0
        if self.currentGameConfig:
            config = self.currentGameConfig
        else:
            config = self.configGames[0]            
        value  = max(config.mouse_convert.limitmin,min(config.mouse_convert.limitmax,xval+lastvalue))
        movement = config.mousexy(value)
        return value, movement, tdif

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def GetNumZeroCrossings(self, data, threshold):
        numcrossings = 0
        curpos = 0                              # -1 = below -thresh
        for i in range(0, len(data)):                        
            if abs(data[i]) > threshold:        # data magnitude is greater than threshold (- or +)
                if data[i] < 0:                 # below -threshold, and curpos above +threshold
                    if curpos > 0:
                        numcrossings += 1           
                    curpos = -1
                elif data[i] > 0:               # above +threshold and curpos below -threshold
                    if curpos < 0:
                        numcrossings += 1          
                    curpos = 1
            else:                               # data is subthreshold
                curpos = 0
        return numcrossings
                                  
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def ComPortThread1(self):
        while self.alive1.isSet():               # loop while alive event is true
            text = self.serial1.read(1)          # read one, with timout
            if text:                             # check if not timeout
                n = self.serial1.inWaiting()     # look if there is more to read
                if n:
                    text = text + self.serial1.read(n) 
                    
                self.serialbuffer.fromstring(text)
                event = SerialRxEvent(self.GetId(), text)
                self.GetEventHandler().AddPendingEvent(event)

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def WiimotePolling(self):
        while self.alive2.isSet():
            wiistat = self.wiimote.poll_wiimote_device()
            if wiistat != 0:
                #ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
                #win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0,0,0)
                userEvent.m_click()

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
    def Reset_Serial_Port(self):
        self.StopThread()
        self.StopThread()
        self.serial1.close()
        self.serialconnected = 0
        self.serialbuffer = pyarray.array('b')                              
        self.EMGbuffer[0] = pyarray.array('B')
        self.EMGbuffer[1] = pyarray.array('B')
        self.EMGbuffer2 = [pyarray.array('B'), pyarray.array('B')]          
        self.dialogSerialConfig.SetPortsFromContent()
        self.serial1.open()
        self.serialconnected = 1             
        self.StartSerialPortThreads()
        print "Re-started serial thread and flushed buffers"

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
if __name__ == "__main__":
    NeuroGame = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = MyFrame(None, -1, "")
    NeuroGame.SetTopWindow(frame_1)
    frame_1.Show()
    NeuroGame.MainLoop()