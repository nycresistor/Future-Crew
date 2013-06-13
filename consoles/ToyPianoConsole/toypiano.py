# toy piano Future Crew client!
#
# toy piano sends midi notes 48 - 72 (C - C - C)

from future_client import FutureClient, Game, MessageSlot
from matrix_orbital_lcd import MatrixOrbitalLCD

import time
import sys

import pygame
import pygame.midi
import pygame.mixer  # sound output


from random import random



class PlayOneNote(Game):
	def __init__(self, controller, whichNote):
		super(PlayOneNote, self).__init__(
			'PlayOneNote'+str(whichNote), 
			controller.noteName(whichNote) + ' ON PIANO!')
	
		self.c = controller
		self.whichNote = whichNote
	
		self.timeLimit = 5.0
		self.warningTime = 2.5
		
		self.GPO_BAD = 1
		self.GPO_GOOD = 3
		
		self.c.lcd.backlight(True)
		self.c.lcd.gpo(self.GPO_BAD,False)
		self.c.lcd.gpo(self.GPO_GOOD,False)
		


	def play_game(self):
		starttime = time.time()
		mistakes = 0
		lost = False
		
		self.c.flushMidi() # make sure there's no old notes queued up
		self.c.lcd.backlight(True) # make sure LCD light is on and not blinking
		self.c.lcd.gpo(self.GPO_BAD,False)
		#self.c.lcd.gpo(self.GPO_GOOD,False) --- DON'T clear the GOOD lamp, let it keep blinking from previous success for a little while
		#self.c.lcd.brightness(128)
		
		while self.is_running():
			if not self.wait(0.05):
				return
				
			if (self.c.midi.poll()):
				message = self.c.midi.read(1)
				if (self.c.matchNotes(self.whichNote, message[0][0][1], 'octave')):
					print 'YES'
					self.c.sound('yes')
					self.c.flushMidi()
					#self.c.lcd.brightness(255)
					self.c.lcd.gpoBlink(self.GPO_GOOD, 0.1, 0.55)
					self.finish(1)
				else:
					print 'NO'
					self.c.sound('no')
					#self.c.lcd.blink(0.1, 0.35)
					self.c.lcd.gpoBlink(1, 0.15, 0.4)
					mistakes += 1
					self.c.flushMidi()
					if (mistakes > 3): self.finish(0)
					
			if ((time.time()-starttime) > self.warningTime):
				#self.c.lcd.blink(0.1)
				self.c.lcd.gpoBlink(self.GPO_BAD, 0.1)
					
			if (not lost and (time.time()-starttime) > self.timeLimit):
				print 'OUT OF TIME'
				lost = True
				self.c.sound('timeout')
				sys.stdout.flush()
				#self.c.lcd.backlight(False)
				self.c.lcd.gpo(self.GPO_BAD,False)
				
			if ((time.time()-starttime) > self.timeLimit + 0.5):
				self.finish(0)





class ToyPianoConsole:
	def __init__(self):
		pygame.init()
		pygame.midi.init()
		self.midi = pygame.midi.Input(3, 0)
		
		self.lcd = MatrixOrbitalLCD()
		
		pygame.mixer.init()
		self.soundList = [
			('yes', 'Alert Tone 22.ogg'),
			('no', 'Exclamation Tone 32.ogg'),
			('timeout', 'Error Tone 37.ogg')
		]
		self.sounds = dict((n, pygame.mixer.Sound('sounds/'+f)) for (n,f) in self.soundList)
		
		self.whiteKeys = [0,2,4,5,7,9,11]
		self.noteNames = {
			'terse': {
				'sharps': ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
				'flats' : ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
			},
			'verbose': {
				'sharps': ['C', 'C SHARP', 'D', 'D SHARP', 'E', 'F', 'F SHARP', 'G', 'G SHARP', 'A', 'A SHARP', 'B'],
				'flats':  ['C', 'D FLAT', 'D', 'E FLAT', 'E', 'F', 'G FLAT', 'G', 'A FLAT', 'A', 'B FLAT', 'B']
			}
		}

	# use up incoming notes
	def flushMidi(self):
		while (self.midi.poll()): self.midi.read(1)

	# name of note from MIDI note number
	def noteName(self, whichNote, accidentals='both', verbose=True):
		n = whichNote % 12
		if (accidentals=='both'):
			if (random() > 0.5): accidentals='flats'
			else: accidentals='sharps'
		if (verbose):
			v = 'verbose'
		else:
			v = 'terse'
		
		return self.noteNames[v][accidentals][whichNote]
	
	
	# play a sound by key
	def sound(self, key):
		if (self.sounds[key]): self.sounds[key].play()
		
	
	# check if note numbers match
	#	 options: exact, octave (match % 12)
	def matchNotes(self, n1, n2, options='octave'):
		if (options=='octave'): return ((n1 % 12) == (n2 % 12))
		elif (options=='exact'): return (n1 == n2)
		else: return False



class SimpleMessageSlot(MessageSlot):
	def __init__(self, slotname):
		self.slotname = slotname
		super(SimpleMessageSlot,self).__init__()
	def on_message(self,text):
		if text:
			print "Simple Slot",self.slotname,"says:",text
		else:
			print "Simple Slot",self.slotname,"has been cleared!"

class LCDMessageSlot(MessageSlot):
	def __init__(self, slotname, lcd):
		self.slotname = slotname
		self.lcd = lcd;
		super(LCDMessageSlot,self).__init__()
	def on_message(self,text):
		if text:
			self.lcd.cls()
			self.lcd.lcdprintln(text)
		else:
			self.lcd.cls()



controller = ToyPianoConsole()


fc = FutureClient(name="ToyPianoClient", urlstring="ws://192.168.1.99:2600/socket")
fc.available_games = [PlayOneNote(controller, i) for i in controller.whiteKeys]
fc.message_slots = [LCDMessageSlot('PrintSlot', controller.lcd)]

fc.start()
try:
	while 1:
		controller.lcd.update()
		time.sleep(0.05)
except:
	fc.quit()


