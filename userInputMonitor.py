#!/usr/bin/env python
# userInputMonitor.py

KEYID_SPACE = 32
KEYID_SHIFTL = 160
KEYID_SHIFTR = 161
KEYID_CTRLL = 162
KEYID_CTRLR = 163
KEYID_ALTL = 164
KEYID_ALTR = 165

KEYID_CAPSLOCK = 165

KEYID_ARROW_UP = 38
KEYID_ARROW_DOWN = 40
KEYID_ARROW_RIGHT = 39
KEYID_ARROW_LEFT = 37 

KEYID_PAGE_UP = 33
KEYID_PAGE_DOWN = 34
KEYID_DEL = 46
KEYID_INS = 45
KEYID_HOME = 36
KEYID_END = 35
KEYID_BACK = 8

KEYID_ENTER = 13

KEYID_PAGE_F1 = 112
KEYID_PAGE_F2 = 113
KEYID_PAGE_F3 = 114
KEYID_PAGE_F4 = 115
KEYID_PAGE_F5 = 116
KEYID_PAGE_F6 = 117
KEYID_PAGE_F7 = 118
KEYID_PAGE_F8 = 119
KEYID_PAGE_F9 = 120
KEYID_PAGE_F10 = 121
KEYID_PAGE_F11 = 122
KEYID_PAGE_F12 = 123

class userInputMonitor:
    def __init__(self):
        self.shift_down = False
        self.alt_down = False
        self.ctrl_down = False
        self.key_down = False
        self.keyID = False
        self.keyascii = False
        
    def update_key_down(self, event): 
        if event.KeyID == KEYID_SHIFTL or event.KeyID == KEYID_SHIFTR:
            if not self.shift_down:
                self.shift_down = True
            return False
        
        elif event.KeyID == KEYID_ALTL or event.KeyID == KEYID_ALTR:
            if not self.alt_down:
                self.alt_down = True
            return False

        elif event.KeyID == KEYID_CTRLL or event.KeyID == KEYID_CTRLR:
            if not self.ctrl_down:
                self.ctrl_down = True
            return False
        
        elif event.KeyID == KEYID_CAPSLOCK:
            return False        

        else:
            self.keyID = event.KeyID
            self.keyascii = event.Ascii
            self.key_down = True
            return event.KeyID

    def update_key_up(self, event):
        if event.KeyID == KEYID_SHIFTL or event.KeyID == KEYID_SHIFTR:
            if self.shift_down:
                self.shift_down = False
            return False
        
        elif event.KeyID == KEYID_ALTL or event.KeyID == KEYID_ALTR:
            if self.alt_down:
                self.alt_down = False
            return False

        elif event.KeyID == KEYID_CTRLL or event.KeyID == KEYID_CTRLR:
            if self.ctrl_down:
                self.ctrl_down = False
            return False

        else:
            self.keyID = event.KeyID
            self.keyascii = event.Ascii
            self.key_down = False
            return event.KeyID
        
        



