# class for a Matrix Orbital LCD display on a serial port
#
#    call update() frequently if you want to use time-based stuff like blink

import serial
import time

class MatrixOrbitalLCD(object):

	# default tty '/dev/ttyAMA0' is the built-in 3.3V serial port on the Pi's GPIO header.  
	#	Connect Pi GND to LCD Gnd and Pi Tx to LCD Rx.  Don't connect Pi Rx to LCD Tx.
	#	It seems to work fine driving the 5V LCD serial input with no 3.3->5V level converter.
	# 	Since we don't care about receiving from LCD, no need to make a level converter for the other direction
	# default baud rate 19200 is the LCD's default baud rate.
	def __init__(self, tty='/dev/ttyAMA0', baud=19200):
		self.port = serial.Serial(tty, baud)
		self.t = time.time()
		self.dt = 0
		self.blinkDuration = 0     # backlight blink duration in seconds
		self.blinkTime = 0 # next blink time
		self.blinkEndTime = 0
		self.backlightState = True
		
		
	# various config stuff  ----
	
	# auto scroll True / False
	def autoScroll(self, flag):
		if (flag):
			self.writeBytes([254,81])
		else:
			self.writeBytes([254,82])
	
	# word wrap True / False
	def autoWrap(self, flag):
		if (flag):
			self.writeBytes([254,67])
		else:
			self.writeBytes([254,68])
			
	# move cursor to X/Y
	def cursorPos(self, x, y):
		self.writeBytes([254,71,x,y])
	
	
	# simple print / println
	def lcdprint(self, text):
		self.port.write(text)
		
	def lcdprintln(self, text):
		self.lcdprint(text + chr(10)+chr(13))
	
	# clear screen
	def cls(self):
		self.port.write(chr(12))
		
	# backlight on / off (True / False) also disables blink
	def backlight(self, flag=True, resetBlink=True):
		if (resetBlink):
			self.blinkDuration = 0
			self.blinkTime = 0
			self.blinkEndTime = 0
			
		self.backlightState = flag
		if (flag):
			self.writeBytes([254,66,0])
		else:
			self.writeBytes([254,70])


	# backlight brightness 0-255
	def brightness(self, b):
		self.writeBytes([254,153,b])
		
	
	# write an array or list of bytes
	def writeBytes(self, bs):
		for b in bs:
			self.port.write(chr(b))



	# blink with on and off time = dur (in seconds) - 0 for no blink (light on)
	#   stop blinking after ... 0 for don't stop
	def blink(self, dur, stopAfter=0):
		if (dur==0): 
			self.backlight(True)
			self.blinkEndTime = 0
		elif stopAfter > 0:
			self.blinkEndTime = self.t + stopAfter
		else:
			self.blinkEndTime = 0
		if (dur != self.blinkDuration):
			self.blinkDuration = dur
			self.blinkTime = self.t

	
	
	# call update() frequently if you want to use time-based stuff like blink
	def update(self):
		t = time.time()
		self.dt = t - self.t
		self.t = t
		#print "dur:" + str(self.blinkDuration) + " endAt:" + str(self.blinkEndTime) + " light:" + str(self.backlightState)
		
		if (self.blinkDuration > 0 and self.blinkEndTime > 0 and t > self.blinkEndTime):
			self.blink(0)
		
		if (self.blinkDuration > 0 and t > self.blinkTime):
			self.backlight(not self.backlightState, resetBlink=False)
			self.blinkTime = t + self.blinkDuration
			
		
		
		
	