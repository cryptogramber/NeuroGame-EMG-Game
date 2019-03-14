#!/usr/bin/env python
# userEvent.py

import win32api
import win32con
from ctypes import windll
import time

def m_move(x,y):
    windll.user32.SetCursorPos(x,y)

def m_scroll(amount):
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, amount, 0)

def m_click():
    x,y = win32api.GetCursorPos()
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

#def m_scroll_reset(skipAmt):
#    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, skipAmt, 0)
#    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, skipAmt, 0)
#    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, skipAmt, 0)
#    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, skipAmt, 0)
#    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, skipAmt, 0)
#    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, skipAmt, 0)

#def l_click(x="current", y="current"):
#    if x == "current" and y == "current":
#        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
#        time.sleep(0.05)
#        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
#    else:
#        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y)
#        time.sleep(0.05)
#        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y)

#def r_click(x="current", y="current"):
#    if x == "current" and y == "current":
#        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
#        time.sleep(0.05)
#        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
#    else:
#        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y)
#        time.sleep(0.05)
#        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y)
