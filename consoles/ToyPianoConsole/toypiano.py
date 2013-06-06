# toy piano Future Crew client!
#
# toy piano sends midi notes 48 - 72 (C - C - C)

from future_client import FutureClient, Game, MessageSlot

import time
import sys

import pygame
import pygame.midi

from random import random



class PlayOneNote(Game):
	def __init__(self, controller, whichNote):
		super(PlayOneNote, self).__init__(
			'PlayOneNote'+str(whichNote), 
			'Quick! Play a ' + controller.noteName(whichNote) + ' note!')
	
		self.c = controller
		self.whichNote = whichNote
	
		self.timeLimit = 5.0


	def play_game(self):
		starttime = time.time()
		mistakes = 0
		
		self.c.flushMidi() # make sure there's no old notes queued up
		
		while self.is_running() and (time.time()-starttime) < self.timeLimit:
			if not self.wait(0.05):
				print 'OUT OF TIME' # this doesn't show up on stdout for some reason, despite the flush
				sys.stdout.flush()
				self.finish(0)
				return
			if (self.c.midi.poll()):
				message = self.c.midi.read(1)
				if (self.c.matchNotes(self.whichNote, message[0][0][1], 'octave')):
					print 'YES'
					self.c.flushMidi()
					self.finish(1)
				else:
					print 'NO'
					mistakes += 1
					self.c.flushMidi()
					if (mistakes > 3): self.finish(0)





class ToyPianoConsole:
	def __init__(self):
		pygame.init()
		pygame.midi.init()
		self.midi = pygame.midi.Input(3, 0)
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



controller = ToyPianoConsole()

fc = FutureClient(name="ToyPianoClient", urlstring="ws://192.168.1.99:2600/socket")
fc.available_games = [PlayOneNote(controller, i) for i in range(12)]
fc.message_slots = [SimpleMessageSlot('PrintSlot')]

fc.start()
try:
	while 1:
		time.sleep(0.05)
except:
	fc.quit()


