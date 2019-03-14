#!/usr/bin/env python
# configGame.py 

import userMacro
import subprocess
import time
import datetime
import numpy

PI = 3.1415927
FUNCTYPE_LINEAR = 0
FUNCTYPE_CIRCLE = 1

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
class mouse_converter:
    def __init__(self, functype=0, radius=0, rangemin=0, rangemax=0, limitmin=0, limitmax=0):
        self.functype = functype
        self.radius = radius
        self.rangemin = rangemin
        self.rangemax = rangemax
        self.limitmin = limitmin
        self.limitmax = limitmax

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~     
    def mousexy(self, value):
        point = [0, 0]
        value = min(max(value,self.limitmin),self.limitmax)
        
        if self.functype == FUNCTYPE_LINEAR:
            point[0] = value
            
        elif self.functype == FUNCTYPE_CIRCLE:
            unitval = (2*PI*(value-self.rangemin)/(self.rangemax-self.rangemin))-PI;
            point[0] = numpy.sin(unitval)*self.radius;
            point[1] = numpy.cos(unitval)*self.radius;
        return point

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
class configGame:
    def __init__(self, gameName='', start_command='', start_macro='',
                 stop_macro='', pause_macro='', mouse_convert=[]):
        self.gameName = gameName
        self.start_command = start_command
        self.start_macro = start_macro
        self.stop_macro = stop_macro
        self.pause_macro = pause_macro
        self.bout_dur = 0
        self.pause_dur = 0
        self.game_proc = False
        self.gameStarted = False
        self.start_time = []
        self.mouse_convert = mouse_convert

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def start_game(self, boutdur=0, pausedur=0):
        if self.game_is_running(): self.self.stop_game()
        self.game_proc = subprocess.Popen(self.start_command)
        userMacro.run(self.start_macro)
        self.gameStarted = True
        self.start_time = datetime.datetime.now()
        return True

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def game_is_running(self):
        if not self.game_proc:
            return False
        if self.game_proc.poll() == None:
            return True
        return False

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def mousexy(self, value):
        point = [0, 0]
        if self.mouse_convert:
            point = self.mouse_convert.mousexy(value)
        else:
            point[0] = value
        return point

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def game_duration(self):
        if not self.start_time:
            return 0
        return (datetime.datetime.now() - self.start_time).seconds

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~                 
    def stop_game(self):
        userMacro.run(self.stop_macro)
        if self.game_is_running(): self.game_proc.kill()
        self.gameStarted = False
        return True

# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~
# ~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~+-~ 
    def pause_game(self):
        userMacro.run(self.pause_macro)
        return True