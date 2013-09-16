#!/usr/bin/python
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


class TinySongGame(Game):
	def __init__(self, controller, song_name, song_notes):
		super(TinySongGame, self).__init__(
			'TinySongGame'+song_name, 
			song_name + ' ON PIANO!')

		self.c = controller
		self.song_name = song_name
		self.song_notes = song_notes
	
		self.timeLimit = 20.0
		self.warningTime = 17.0
		
		self.GPO_BAD = 1
		self.GPO_GOOD = 3
		
		self.c.lcd.backlight(True)
		self.c.lcd.gpo(self.GPO_BAD,False)
		self.c.lcd.gpo(self.GPO_GOOD,False)		
		
	def play_game(self):
		starttime = time.time()
		mistakes = 0
		match_idx = 0
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
				if (self.c.matchNotes(self.song_notes[match_idx], message[0][0][1], 'octave')):
					match_idx += 1
					if match_idx == len(self.song_notes):
						print 'YES'
						self.c.sound('yes')
						self.c.flushMidi()
						#self.c.lcd.brightness(255)
						self.c.lcd.gpoBlink(self.GPO_GOOD, 0.1, 0.55)
						self.finish(1)
				else:
					match_idx = 0
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
		

class PlayChords(Game):
    def __init__(self, controller, whichChord, key):
        super(PlayChords, self).__init__(
            'PlayChords'+str(whichChord), 
            controller.chordName(whichChord, key) + ' CHORD ON PIANO!')

        self.controller = controller
        self.correctChord = self.controller.getChordSequence(whichChord, key) 

        self.timeLimit = 8.0
        self.warningTime = 4.0

        self.GPO_BAD = 1
        self.GPO_GOOD = 3

        self.controller.lcd.backlight(True)
        self.controller.lcd.gpo(self.GPO_BAD,False)
        self.controller.lcd.gpo(self.GPO_GOOD,False)


    def play_game(self):
        starttime = time.time()
        mistakes = 0
        lost = False

        self.controller.flushMidi() # make sure there's no old notes queued up
        self.controller.lcd.backlight(True) # make sure LCD light is on and not blinking
        self.controller.lcd.gpo(self.GPO_BAD,False)

        while self.is_running():
            if not self.wait(0.05):
                return
                
            if (self.controller.midi.poll()):
                you_lost = False
                message = self.controller.midi.read(3)
                if len(message) == len(self.correctChord):
                    chord = [message[0][0][1] , message[1][0][1], message[2][0][1]]
                    if (self.controller.matchChords(self.correctChord, chord)):
                        print 'YES'
                        self.controller.sound('yes')
                        self.controller.flushMidi()
                        self.controller.lcd.gpoBlink(self.GPO_GOOD, 0.1, 0.55)
                        self.finish(1)
                    else:
                        you_lost = True
                else:
                    you_lost = True
                
                if you_lost == True:
                    print 'NO'
                    self.controller.sound('no')
                    self.controller.lcd.gpoBlink(1, 0.15, 0.4)
                    mistakes += 1
                    self.controller.flushMidi()
                    if (mistakes > 3): self.finish(0)

                    
            if ((time.time()-starttime) > self.warningTime):
                self.controller.lcd.gpoBlink(self.GPO_BAD, 0.1)
                    
            if (not lost and (time.time()-starttime) > self.timeLimit):
                print 'OUT OF TIME'
                lost = True
                self.controller.sound('timeout')
                sys.stdout.flush()
                self.controller.lcd.gpo(self.GPO_BAD,False)
                
            if ((time.time()-starttime) > self.timeLimit + 0.5):
                self.finish(0)

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
		self.allKeys = range(0, 12)
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

	def chordName(self, whichNote, key='both', accidentals='flats', verbose=False):
		note = self.noteName(whichNote, accidentals, verbose)
		if (key=='both'):
			if (random() > 0.5): key='MAJOR'
			else: key='MINOR'
		
		return (note + " " + key)

		
	# play a sound by key
	def sound(self, key):
		if (self.sounds[key]): self.sounds[key].play()
		
	def getChordSequence(self, whichChord, key):
		if key == 'MAJOR':
			chord_sequence = [whichChord, (whichChord+4) % 12, (whichChord+7) % 12]
		else: 
			chord_sequence = [whichChord, (whichChord+3) % 12, (whichChord+7) % 12]
		return chord_sequence
	
	# check if note numbers match
	#	 options: exact, octave (match % 12)
	def matchNotes(self, n1, n2, options='octave'):
		if (options=='octave'): return ((n1 % 12) == (n2 % 12))
		elif (options=='exact'): return (n1 == n2)
		else: return False

	def matchChords(self, list1, list2):
		for i in range(0,len(list2)):
			list2[i] = list2[i] % 12
		return sorted(list1) == sorted(list2)



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

songs = [  #("ROW YOUR BOAT",   [0, 0, 0, 2, 4]),       # Row Row Row Your Boat - C C C D E
		 ("E-I-E-I-O",       [4, 4, 2, 2, 0]),       # E-I-E-I-O - E E D D C
		 ("FRERE JACQUES",   [7, 9, 11, 7]),         # Frere Jacques - G A B G
		 ("TWINKLE TWINKLE", [7, 7, 2, 2]),          # Twinkle Twinkle Little Star - G G D D 
		 ("ALOUETTE",        [0, 2, 4, 4]),          # Alouette - C D E E 
		 ("BEETHOVEN",       [9, 9, 9, 5]),          # Beethoven's 5th - A A A F
		 #("HAPPY BIRTHDAY",  [2, 2, 4, 2, 7, 5]),    # Happy Birthday - D D E D G F
		]

chords = [  [0, 'MAJOR'],
            [4, 'MAJOR'],
            [9, 'MAJOR'],
            [2, 'MINOR'],
          #  [7, 'MINOR'],
            [5, 'MINOR'] ] 

fc = FutureClient(name="ToyPianoClient", urlstring="ws://192.168.1.99:2600/socket")
fc.available_games = [PlayOneNote(controller, i) for i in controller.allKeys] + [TinySongGame(controller, i[0], i[1]) for i in songs] + [PlayChords(controller, i[0], i[1]) for i in chords]
     
fc.message_slots = [LCDMessageSlot('PrintSlot', controller.lcd)]

fc.start()
try:
	while 1:
		controller.lcd.update()
		time.sleep(0.05)
except:
	fc.quit()


