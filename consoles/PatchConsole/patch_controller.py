from future_client import FutureClient, Game, MessageSlot
import serial
#import serial.tools.list_ports as list_ports
import time
import struct
import threading
import random

class Controller:
    def __init__(self):
	self.cons = {}
        self.port = serial.Serial("/dev/ttyACM0", timeout=3)

    def get_patches(self):
        keys = self.port.readline().strip()
	if not keys:
	    return
	print keys
	cons = keys.split(' ')
	self.switches = cons[0]
	con_map = {}
	for con in cons[1:]:
		fromto = con.split(':')
		#print fromto[0], '=>', fromto[1]
		con_map[fromto[0]] = fromto[1]
	self.cons = con_map
        return

class PatchAtoBGame(Game):
    def __init__(self,c):
        super(PatchAtoBGame, self).__init__('a2b','Patch A to B')
        self.c = c
	self.patch_from = '1A'
	self.patch_to = '1F'

    def play_game(self):
	while 1:
	    if (self.c.cons.get(self.patch_from,'') != self.patch_to):
		continue

	    print "Success!"
	    self.finish(5)
	    return

    def on_start(self):
        t = threading.Thread(target = self.play_game)
        self.thread = t
        t.start()

class StdoutSlot(MessageSlot):
    def __init__(self, c, id=None, length=40):
        self.c = c
        super(StdoutSlot, self).__init__(id,length)

    def on_message(self,text):
	print "Message: ", text

c = Controller()

games = [
    PatchAtoBGame(c),
]

slots = [
    StdoutSlot(c),
]

import sys

if __name__ == '__main__' and len(sys.argv) == 1:
    fc = FutureClient('ws://192.168.1.99:2600/socket','PatchConsole')
    #fc = FutureClient(name='PatchConsole')
    fc.available_games = games
    fc.message_slots = slots
    fc.start()
    try:
	while True:
	    c.get_patches()
	    time.sleep(0.05)
    except:
	fc.quit()
else:
    # test mode
    # do nothing
    print "test"
