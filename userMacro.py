#!/usr/bin/env python
# userMacro.py

import win32api, win32con
import wx
import time
import SendKeys
import os
import subprocess

def mouse_click_abs(button, x, y):
    win32api.SetcursorPosition((x,y))
    if button == 0: # left button
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
    elif button == 1: # right button
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)
    
def mouse_click_scaled(button, x, y):
    displaysize = screen_dimensions()
    x = int(x*displaysize[0])
    y = int(y*displaysize[1])
    mouse_click_abs(button, x, y)
        
def mouse_move_abs(x, y):
    win32api.SetcursorPosition((x,y))
   
def mouse_move_scaled(x, y):
    displaysize = screen_dimensions()
    x = int(x*displaysize[0])
    y = int(y*displaysize[1])
    mouse_move_abs(x, y)

def mouse_scroll(amount):
    print "mouse_scroll(%r)" % (amount,)
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, amount, 0)
    
def key_send(keystr):
    SendKeys.SendKeys(keystr)

def wait(waitdur):
    time.sleep(waitdur)
    
def screen_dimensions():
    return [win32api.GetSystemMetrics(0),win32api.GetSystemMetrics(1)]        

def os_execute(execstr):
    p = subprocess.Popen(execstr)

def run(commandlist):
    for command in commandlist:
        if command:
            exec(command)