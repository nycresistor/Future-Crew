#!/usr/bin/python
#
# Octoscroller message display
#
from future_client import FutureClient, Game, MessageSlot
import serial
import time
import struct
import threading
import random
import Image, ImageFont, ImageDraw
import socket
import time, datetime

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = ("localhost", 9999)

width = 256
disp = Image.new("RGB", (256,16), "black")
draw = ImageDraw.Draw(disp)
font = ImageFont.truetype("spincycle.ttf", 24)


def show_message(c,s):
	disp.paste("black", (0,0,width,16))
	draw.text((0, -4), s, font=font, fill=c)

	# Slice a 256 size image from the large image
	sock.sendto(chr(1) + disp.tostring(), dest)

#import console_locations

class Controller:
    def __init__(self):
	self.cons = {}


c = Controller()
games = []
slots = []

class OctoscrollerClient(FutureClient):
    def __init__(self,controller):
        self.c = controller
        super(OctoscrollerClient,self).__init__('ws://192.168.1.99:2600/socket', name='OctoscrollerConsole')

    def on_session_start(self,message):
        #slots[0].on_session_start(message)
	show_message("white", "FUTURE CREW START");

    def on_session_fail(self,message,score):
	show_message("red", "YOUR FUTURE CREW HAS FAILED")

    def on_session_success(self,message,score):
	show_message("blue", "FUTURE CREW WINS")
        #slots[0].on_session_success(message)


import sys

if __name__ == '__main__' and len(sys.argv) == 1:
    fc = OctoscrollerClient(c)
    fc.available_games = games
    fc.message_slots = slots
    fc.start()
    try:
	while True:
	    time.sleep(0.05)
    except:
	print "except"
	fc.quit()
else:
    # test mode
    # do nothing
    print "test"
