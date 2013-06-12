import serial
import time
import struct
import threading
import random
from patches import *

port = serial.Serial("/dev/tty.usbmodem12341", timeout=3)

oldsw = 0

while 1:
	keys = port.readline().strip()
	if not keys:
	    next

	#print keys

	cons = keys.split(' ')

	sw = int(cons[0], 16)
	sw &= ~0x80; # switch 8 is flaky
	for i in range(0,8):
		val = (sw >> i) & 1
		if ((oldsw >> i) & 1) ^ val:
			print "Switch: ", switches[i], 'ON' if val else 'OFF'
	oldsw = sw

	for con in cons[1:]:
		fromto = con.split(':')
		#print fromto[0], '=>', fromto[1]
		print "Patched: ", \
			patches[fromto[0]], \
			" to ", \
			patches[fromto[1]]
