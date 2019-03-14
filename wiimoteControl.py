#!/usr/bin/env python
# wiimoteControl.py

import ctypes
import wiiuse
import sys, time, os

class wiimoteControl:
    def __init__(self):
        self.nmotes = 1
        self.wiimotes = wiiuse.init(self.nmotes)

        found = wiiuse.find(self.wiimotes, self.nmotes, 5)
        if not found:
            print 'wiimote not found'

        connected = wiiuse.connect(self.wiimotes, self.nmotes)
        if connected:
            print 'Connected to %i wiimotes (of %i found).' % (connected, found)
        else:
            print 'failed to connect to any wiimote.'

        for i in range(self.nmotes):
            wiiuse.set_leds(self.wiimotes[i], wiiuse.LED[i])
            wiiuse.status(self.wiimotes[0])

    #def handle_event(self,wmp):
    #    wm = wmp[0]
    #    #ctypes.windll.user32.SetcursorPositionition(self.screensize1, self.screensize2)
    #    ctypes.windll.user32.mouse_event(2, 0, 0, 0,0) # left down
    #    #ctypes.windll.user32.mouse_event(4, 0, 0, 0,0) # left up

    ##    if wm.btns:
    ##        ctypes.windll.user32.mouse_event(2, 0, 0, 0,0) # left down
    ##        ctypes.windll.user32.mouse_event(4, 0, 0, 0,0) # left up
    ##        for name, b in wiiuse.button.items():
    ##            if wiiuse.is_pressed(wm, b):
    ##                print name,'pressed'
    ##
    ##        if wiiuse.is_just_pressed(wm, wiiuse.button['-']):
    ##        if wiiuse.is_just_pressed(wm, wiiuse.button['+']):
    ##            wiiuse.motion_sensing(wmp, 1)
    ##        if wiiuse.is_just_pressed(wm, wiiuse.button['B']):
    ##            wiiuse.toggle_rumble(wmp)
    ##        if wiiuse.is_just_pressed(wm, wiiuse.button['Up']):
    ##            wiiuse.set_ir(wmp, 1)
    ##        if wiiuse.is_just_pressed(wm, wiiuse.button['Down']):
    ##            wiiuse.set_ir(wmp, 0)
    
    def handle_ctrl_status(self, wmp, attachment, speaker, ir, led, battery_level):
        wm = wmp[0]
        print '--- Controller Status [wiimote id %i] ---' % wm.unid
        print 'attachment', attachment
        print 'speaker', speaker
        print 'ir', ir
        print 'leds', led[0], led[1], led[2], led[3]
        print 'battery', battery_level

    def handle_disconnect(self, wmp):
        print 'disconnect'

    def poll_wiimote_device(self):
        r = wiiuse.poll(self.wiimotes, self.nmotes)
        #if r != 0:
        #    self.handle_event(self.wiimotes[0])
        return r

    def shut_down_wiimote(self):
        for i in range(self.nmotes):
            wiiuse.set_leds(self.wiimotes[i], 0)
            wiiuse.rumble(self.wiimotes[i], 0)
            wiiuse.disconnect(self.wiimotes[i])