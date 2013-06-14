
import pygame
import pygame.midi
import pygame.mixer  # sound output


class ToyPianoConsole:
    def __init__(self, whichChord):
        pygame.init()
        pygame.midi.init()
        self.midi = pygame.midi.Input(3, 0)

        pygame.mixer.init()

        self.whichChord = whichChord

    def get_tones(self):
        message = self.controller.midi.read(3)
        print message
        chord = [message[0][0][1], message[0][1][1], message[0][2][1]]
        print chord
        if (self.matchChords(self.getMajorChordSequence(self.whichChord), message[0][0][1], 'octave')):
            print "yes"
        else:
            print "no"

    def getMajorChordSequence(self, whichChord):
        chord_sequence = [whichChord, whichChord+4, whichChord+7]
        return chord_sequence

    def getMinorChordSequence(self, whichChord):
        chord_sequence = [whichChord, whichChord+3, whichChord+7]
        return chord_sequence

    def matchChords(self, list1, list2):
        if len(list1) == len(list2):
            return sorted(list1) == sorted(list2)
        else:
            return False     

if __name__=="__main__":

    piano = ToyPianoConsole(1)
    while(1):
       piano.get_tones()
       sleep(1)


