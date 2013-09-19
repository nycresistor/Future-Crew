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
from colorsys import hsv_to_rgb

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dest = ("localhost", 9999)

width = 256
logo = Image.open("nycr.png")
disp = Image.new("RGB", (256,16), "black")
im = Image.new("RGB", (256,16), "black")
im_draw = ImageDraw.Draw(im)
font = ImageFont.truetype("spincycle.ttf", 24)

timeout = 0
game_over = True
scrolling = True
scroll_offset = 128
rainbow_cycle = 0

def rainbow(i):
	rgb = [int(x*256) for x in hsv_to_rgb(i/1024.0,0.8,0.8)]
	return (rgb[0],rgb[1],rgb[2])

def show_message(c,s):
	im.paste("black", (0,0,width,16))
	im_draw.text((0, -4), s, font=font, fill=c)

def send_image():
	global scroll_offset
	if scrolling:
		disp.paste(im.crop((0,0,scroll_offset,16)), (width-scroll_offset,0))
		disp.paste(im.crop((scroll_offset+1,0,width-1,16)), (0,0))
		scroll_offset = (scroll_offset + 1) % width
	else:
		disp.paste(im, (0,0))
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
	global scrolling, game_over, timeout
	scrolling = True
	game_over = False
	timeout = 200
	print("Received message: '" + message + "'")
	show_message("white", message)

    def on_session_fail(self,message,score):
	global scrolling, game_over, timeout
	scrolling = True
	game_over = True
	timeout = 200
	print("fail message: '" + message + "'")
	show_message("red", message)

    def on_session_success(self,message,score):
	global scrolling, game_over, timeout
	scrolling = True
	game_over = True
	timeout = 200
	show_message("blue", message)
	print("success message: '" + message + "'")
        #slots[0].on_session_success(message)

    def on_announcement(self,msg):
	global scrolling, game_over, timeout
	#scrolling = True
	#game_over = True
	#timeout = 200
	print "msg: " + msg

import sys

if __name__ == '__main__' and len(sys.argv) == 1:
    scrolling = True
    scroll_offset = 0
    show_message("blue", "  FUTURE CREW: WAIT")
    im.paste(logo, (0,0))
    send_image()

    fc = OctoscrollerClient(c)
    fc.available_games = games
    fc.message_slots = slots
    fc.start()
    try:
	while True:
 	    if timeout > 0:
		# Just keep showing stuff
		timeout = timeout - 1
		if timeout == 0:
			# Blank the screen
			show_message("black", "")
	    elif game_over:
		# Attract mode; flash stuff
		show_message(rainbow(rainbow_cycle), "  Play Future   Crew!")
	        im.paste(logo, (0,0))
	        im.paste(logo, (170,0))
		rainbow_cycle = (rainbow_cycle + 1) % 1024;
	    send_image()
	    time.sleep(0.05)
    except:
	print "except"
	fc.quit()
else:
    # test mode
    # do nothing
    print "test"
