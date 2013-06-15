
from future_client import FutureClient, Game, MessageSlot
from matrix_orbital_lcd import MatrixOrbitalLCD

import time
import sys
import serial

from random import random


class OneDigitGame(Game):
    def __init__(self, controller, digit):
        super(OneDigitGame, self).__init__(
            'OneDigitGame'+str(digit), 
            'Dial '+str(digit)+'!')

        self.c = controller
        self.digit = digit
    
        self.timeLimit = 7.0
        self.warningTime = 5.0
        
        self.c.lcd.backlight(True)
      
        
    def play_game(self):
        starttime = time.time()
        mistakes = 0
        lost = False
        
        self.c.lcd.backlight(True) # make sure LCD light is on and not blinking
 
        while self.is_running():
            if not self.wait(0.05):
                return
            
            input_digit = self.c.get_digit()    
            if input_digit:
                if input_digit == self.digit:
                    print 'YES'
                    self.finish(1)
                else:
                    print 'NO'
                    mistakes += 1
                    if (mistakes > 3): self.finish(0)
                    
            if (not lost and (time.time()-starttime) > self.timeLimit):
                print 'OUT OF TIME'
                lost = True
                sys.stdout.flush()
                                
            if ((time.time()-starttime) > self.timeLimit + 0.5):
                self.finish(0)        

class PhonebookGame(Game):
    def __init__(self, controller, person_name, person_number):
        super(PhonebookGame, self).__init__(
            'PhonebookGame'+person_name, 
            'Dial '+ person_name + ' !')

        self.c = controller
        self.person_name = person_name
        self.person_number = person_number
    
        self.timeLimit = 12.0
        self.warningTime = 10.0
        
        self.c.lcd.backlight(True)     
        
    def play_game(self):
        starttime = time.time()
        mistakes = 0
        match_idx = 0
        lost = False
        
        self.c.lcd.backlight(True) # make sure LCD light is on and not blinking

        while self.is_running():
            if not self.wait(0.05):
                return
                
            input_digit = self.c.get_digit()    
            if input_digit:
                 if input_digit == self.person_number[match_idx]:
                    match_idx += 1
                    if match_idx == len(self.person_number):
                        print 'YES'
                        self.finish(1)
                 else:
                    match_idx = 0
                    print 'NO'
                    mistakes += 1
                    if (mistakes > 3): self.finish(0)
                    
                    
            if (not lost and (time.time()-starttime) > self.timeLimit):
                print 'OUT OF TIME'
                lost = True
                sys.stdout.flush()
                
            if ((time.time()-starttime) > self.timeLimit + 0.5):
                self.finish(0)    


class RotaryConsole:
    def __init__(self):
        self.cons = {}
        self.port = serial.Serial("/dev/ttyUSB0", timeout=3)
        self.lcd = MatrixOrbitalLCD()

    def get_digit(self):
        digit = self.port.readline().strip()
        if not digit or not digit.isdigit():
            return None
        return int(digit)
        


class SimpleMessageSlot(MessageSlot):
    def __init__(self, slotname):
        self.slotname = slotname
        super(SimpleMessageSlot,self).__init__()
    def on_message(self,text):
        if text:
            print "Simple Slot",self.slotname,"says:",text
        else:
            print "Simple Slot",self.slotname,"has been cleared!"

class LCDMessageSlot(MessageSlot):
    def __init__(self, slotname, lcd):
        self.slotname = slotname
        self.lcd = lcd;
        super(LCDMessageSlot,self).__init__()
    def on_message(self,text):
        if text:
            self.lcd.cls()
            self.lcd.lcdprintln(text)
        else:
            self.lcd.cls()

controller = RotaryConsole()

people = [("the President", [3, 4, 7]),
          ("the NSA", [1, 8, 4]),
          ("LOL", [5, 6, 5]),
          ("WTF", [9, 8, 3]),
          ("the NSA", [6, 7, 2]),
          ("the FBI", [3, 2, 4]),
          ("the KGB", [5, 4, 2]),
          ("the A-Team", [6, 7, 8]),
          ("your lawyer", [5, 4, 3, 7]),
          ("Bill and Ted", [9, 4, 6, 2]),
          ("not found", [4, 0, 4]),
          ("James Bond", [0, 0, 7]),
          ("your mother", [6, 6, 6]),
          ("Moviefone", [4, 1, 1]),
          ("Razor and Blade", [1, 3, 3, 7]),
          ("Emmanuel Goldstein", [2, 6, 0, 0]),
          ("the Devil", [6, 6, 6]),
          ("Jenny", [8, 6, 7, 5, 3, 0, 9]),
          ("M", [6]),
          ("the Ghostbusters", [6, 0, 2])]

fc = FutureClient(name="ToyPianoClient", urlstring="ws://192.168.1.99:2600/socket")
fc.available_games = [OneDigitGame(controller, i) for i in range(1, 11)] +  [PhonebookGame(controller, i[0], i[1]) for i in people] 
fc.message_slots = [LCDMessageSlot('PrintSlot', controller.lcd)]

fc.start()
try:
    while 1:
        controller.lcd.update()
        time.sleep(0.05)
except:
    fc.quit()


