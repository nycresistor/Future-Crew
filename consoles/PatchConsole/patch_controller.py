from future_client import FutureClient, Game, MessageSlot
import serial
#import serial.tools.list_ports as list_ports
import time
import struct
import threading
import random
import patches
from random import randint

class Controller:
    def __init__(self):
	self.cons = {}
        self.port = serial.Serial("/dev/tty.usbmodem12341", timeout=3)

    def get_patches(self):
        keys = self.port.readline().strip()
	if not keys:
	    return
	#print keys
	cons = keys.split(' ')
	self.switches = int(cons[0], 16) & ~0x80
	con_map = {}
	for con in cons[1:]:
		fromto = con.split(':')
		#print fromto[0], '=>', fromto[1]
		con_map[fromto[0]] = fromto[1]
	self.cons = con_map
        return

class PatchVerbGame(Game):
    def __init__(self,c):
        super(PatchVerbGame, self).__init__('a2b','Patch A to B')
        self.c = c

    def play_game(self):
	self.patch_from = random.choice(patches.verb_patches.keys())
	self.patch_to = random.choice(patches.noun_patches.keys())
	self.update_message(patches.verb_patches[self.patch_from] + " the " + patches.noun_patches[self.patch_to])

        starttime = time.time()
        while self.is_running() and (time.time()-starttime) < 10.0:
	    if (self.c.cons.get(self.patch_from,'') != self.patch_to):
		continue

	    print "Success!"
	    self.finish(5)
	    return
	print "Failure!"
	self.finish(-5)

    def on_start(self):
        t = threading.Thread(target = self.play_game)
        self.thread = t
        t.start()

#
# Simple game to switch off all the blender modes
#
class AllOffGame(Game):
    def __init__(self,c):
        super(AllOffGame, self).__init__('alloff','Disable all blender switches!')
        self.c = c

    def play_game(self):
	if (self.c.switches == 0):
		self.finish(0)
		return
        starttime = time.time()
        while self.is_running() and (time.time()-starttime) < 10.0:
	    if (self.c.switches != 0):
		continue

	    print "All switches off!"
	    self.finish(5)
	    return
	print "Failure!"
	self.finish(-5)

    def on_start(self):
        t = threading.Thread(target = self.play_game)
        self.thread = t
        t.start()

class ToggleSwitchGame(Game):
    def __init__(self,c):
        super(ToggleSwitchGame, self).__init__('sw','Toggle switch')
        self.c = c

    # Should randomly select from a range of choices
    # be sure that it is the opposite of the current value
    def operation(self,val):
	if (val):
		return "Disable"
	else:
		return "Engage"

    def play_game(self):
	self.sw_num = randint(0,6)
	self.start_value = self.c.switches & (1 << self.sw_num)
 	sw_name = patches.switches[self.sw_num]
	print sw_name, ": ", str(self.start_value)
	self.update_message(self.operation(self.start_value) + ' ' + sw_name)

        starttime = time.time()
        while self.is_running() and (time.time()-starttime) < 10.0:
	    if (self.c.switches & (1 << self.sw_num) == self.start_value):
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
	print "M: ", text

c = Controller()

games = [
    PatchVerbGame(c),
    ToggleSwitchGame(c),
    AllOffGame(c)
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
