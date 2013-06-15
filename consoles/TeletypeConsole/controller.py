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
        self.port = serial.Serial("/dev/ttyACM0", timeout=1)
	self.button_map = {}
	for i in range(0,10):
		self.port.write(chr(ord('A') + i))
		time.sleep(0.1)
		self.port.write(chr(ord('a') + i))

    def get_buttons(self):
	#self.update_leds()
        keys = self.port.readline().strip()
	if not keys:
	    return
	print keys
	button_map = {}
	for b in keys.split(' '):
		button_map[int(b)] = 1
	self.button_map = button_map
        return

class PressButtonGame(Game):
    def __init__(self,c):
        super(PressButtonGame, self).__init__('pressbutton', time=5)
	self.led_state = -1
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
	#return random.choice(self.verbs) + ' ' + x
	return x

    def update_leds(self):
	if (self.led_state == -1):
	    self.led_state = random.randint(0,10)
	    self.c.port.write(chr(ord('A') + self.led_state))
	else:
	    self.c.port.write(chr(ord('a') + self.led_state))
	    self.led_state = -1

    def play_game(self):
	self.desired = random.choice(teletype_buttons.buttons.keys())
        self.c.port.write(chr(ord('A') + self.desired))
	print "desired: " + str(self.desired)
	self.update_message(teletype_buttons.buttons[self.desired])
	self.c.port.write(chr(ord('a') + self.desired))

	start_time = time.time()
        while self.is_running() and (time.time() - start_time < 10):
	    self.update_leds()
	    if (self.c.button_map.get(self.desired, 0) == 0):
		self.wait(0.05)
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

class TeletypeSlot(MessageSlot):
    def __init__(self, c, id=None, length=60):
        super(TeletypeSlot, self).__init__(id,length, slow=True)
        self.c = c
        self.port = serial.Serial("/dev/ttyACM1", timeout=1)

    def on_message(self,text):
	if (text):
		print "Teletyping: ", text
		self.port.write(' ' + text)
	else:
		print "Done"
		self.port.write('\r\n')

    def on_session_start(self,text):
	print "New session: ", text
	self.port.write("\r\n### New game ####\r\n")

    def on_session_fail(self,text):
	print "FAIL"
	self.port.write("\r\n### GAME LOST ####\r\n")

    def on_session_success(self,text):
	print "WIN"
	self.port.write("\r\n### YOUR FUTURE CREW HAS WON! ####\r\n")

c = Controller()

games = [
    PressButtonGame(c),
]

slots = [
    TeletypeSlot(c),
]

class TeletypeClient(FutureClient):
    def __init__(self,controller):
        self.c = controller
        super(TeletypeClient,self).__init__('ws://192.168.1.99:2600/socket', name='TeletypeConsole')

    def on_session_start(self,message):
        slots[0].on_session_start(message)

    def on_session_fail(self,message,score):
        slots[0].on_session_fail(message)

    def on_session_success(self,message,score):
        slots[0].on_session_success(message)


import sys

if __name__ == '__main__' and len(sys.argv) == 1:
    #fc = FutureClient('ws://192.168.1.99:2600/socket','TeletypeConsole')
    fc = TeletypeClient(c)
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
