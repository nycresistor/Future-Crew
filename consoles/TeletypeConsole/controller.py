#!/usr/bin/python
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
port = serial.Serial("/dev/ttyACM0", timeout=0.01)

class Controller:
    def __init__(self):
	self.cons = {}
	self.read = ""
        #self.port = serial.Serial("/dev/tty.usbmodem12341", timeout=1)

    def get_buttons(self):
	key = port.readline()
	if not key:
	    return
	print "read: '" + key + "'"
	self.read = self.read + key
	port.write(key)
        return

class PressButtonGame(Game):
    def __init__(self,c):
        super(PressButtonGame, self).__init__('pressbutton', time=5)
        self.c = c
	self.target = None

    def play_game(self):
	self.desired = random.choice(teletype_buttons.buttons)
	self.update_message("TX " + self.desired)
	print "desired: " + self.desired
	self.desired = self.desired.lower()

	start_time = time.time()
        while self.is_running() and (time.time() - start_time < 10):
		if not self.c.read.endswith(self.desired + " "):
			self.wait(0.05)
			continue
		print "Button Success! (read '" + self.c.read + "')"
		self.c.read = ""
		self.finish(5)
		port.write(" OK\r\n")
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

    def on_message(self,text):
	if (text):
		print "Teletyping: ", text
		port.write(' ' + text)
	else:
		print "Done"
		port.write('\r\n')

    def on_session_start(self,text):
	print "New session: ", text
	port.write("\r\n### New game ###\r\n")

    def on_session_fail(self,text):
	print "FAIL"
	port.write("\r\n### GAME LOST ###\r\n")

    def on_session_success(self,text):
	print "WIN"
	port.write("\r\n### YOUR FUTURE CREW HAS WON! ###\r\n")

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
