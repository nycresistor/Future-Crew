# toy piano Future Crew client!
#
# toy piano sends midi notes 48 - 72 (C - C - C)

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

fc = FutureClient(name="ToyPianoClient", urlstring="ws://192.168.1.99:2600/socket")
fc.available_games = [OneDigitGame(controller, i) for i in range(1, 11)]
fc.message_slots = [LCDMessageSlot('PrintSlot', controller.lcd)]

fc.start()
try:
    while 1:
        controller.lcd.update()
        time.sleep(0.05)
except:
    fc.quit()


