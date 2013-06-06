from future_client import FutureClient, Game, MessageSlot
import serial
import serial.tools.list_ports as list_ports
import time
import struct
import threading
import random

class Controller:
    def __init__(self):
        self.port = serial.Serial("/dev/ttyACM0", timeout=3)

    def get_patches(self):
        keys = self.port.readline().strip()
	print keys
        return

class PatchAtoB(Game):
    def __init__(self,c):
        super(PatchAtoB, self).__init__('a2b','Patch A to B')
        self.c = c

    def play_game(self):
	return

    def on_start(self):
        t = threading.Thread(target = self.play_game)
        self.thread = t
        t.start()

class StdoutSlot(MessageSlot):
    def __init__(self, c, id=None, length=40):
        self.c = c
        super(Stdoutlot, self).__init__(id,length)

    def on_message(self,text):
	print "Message", text

c = Controller()

games = [
    PatchAtoBGame(c),
]

slots = [
    StdoutSlot(c),
]

import sys

if __name__ == '__main__' and len(sys.argv) == 1:
    fc = FutureClient('ws://localhost:8888/socket','PatchConsole')
    fc.available_games = games
    fc.message_slots = slots
    fc.start()
    while True:
        try:
            time.sleep(0.05)
        except:
            fc.quit()
            break
else:
    # test mode
    # do nothing
    print "test"
