#
# Teletype and pushbutton interface
#
from future_client import FutureClient, Game, MessageSlot
import serial
import time
import struct
import threading
import random

import teletype_buttons

class Controller:
    def __init__(self):
	self.cons = {}
        #self.port = serial.Serial("/dev/tty.usbmodem12341", timeout=1)
        self.port = serial.Serial("/dev/ttyACM1", timeout=1)
	self.led_state = -1
	self.button_map = {}
	for i in range(0,10):
		self.port.write(chr(ord('A') + i))
		time.sleep(0.1)
		self.port.write(chr(ord('a') + i))

    def update_leds(self):
	if (self.led_state == -1):
	    self.led_state = random.randint(0,10)
	    self.port.write(chr(ord('A') + self.led_state))
	else:
	    self.port.write(chr(ord('a') + self.led_state))
	    self.led_state = -1

    def get_buttons(self):
	self.update_leds()
        keys = self.port.readline().strip()
	if not keys:
	    return
	#print keys
	buttons = keys.split(' ')
	button_map = {}
	for b in buttons[1:]:
		button_map[b] = 1
	self.button_map = button_map
        return

class PressButtonGame(Game):
    def __init__(self,c):
        super(PressButtonGame, self).__init__('pressbutton','Press a button')
        self.c = c
    	self.verbs = [
	    'Press',
	    'Push',
	    'Engage',
	    'Activate',
	    'Bonk',
	    'Enable',
	]


    def verb(self,x):
	return random.choice(self.verbs) + ' ' + x

    def play_game(self):
	self.desired = random.choice(teletype_buttons.buttons.keys())
	print "desired: " + self.desired
	self.update_message(self.verb(teletype_buttons.buttons[self.desired]))

        starttime = time.time()
	
        while self.is_running() and (time.time()-starttime) < 5.0:
	    if (self.c.button_map.get(self.desired, 0) == 0):
		continue

	    self.c.port.write(chr(ord('A') + self.desired))
	    print "Button Success!"
	    self.finish(5)
	    self.c.port.write(chr(ord('a') + self.desired))
	    return
	print "Failure!"
	self.finish(-5)

    def on_start(self):
        t = threading.Thread(target = self.play_game)
        self.thread = t
        t.start()

class StdoutSlot(MessageSlot):
    def __init__(self, c, id=None, length=40):
        self.c = c
        super(StdoutSlot, self).__init__(id,length)

    def on_message(self,text):
	print "M: ", text

c = Controller()

games = [
    PressButtonGame(c),
]

slots = [
    StdoutSlot(c),
]

import sys

if __name__ == '__main__' and len(sys.argv) == 1:
    fc = FutureClient('ws://192.168.1.99:2600/socket','TeletypeConsole')
    fc.available_games = games
    fc.message_slots = slots
    fc.start()
    try:
	while True:
	    c.get_buttons()
	    #time.sleep(0.05)
    except:
	print "except"
	fc.quit()
else:
    # test mode
    # do nothing
    print "test"
