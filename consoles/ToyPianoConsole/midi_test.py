
import pygame
import pygame.midi
import pygame.mixer  # sound output
import time


class ToyPianoConsole:
    def __init__(self, whichChord):
        pygame.init()
        pygame.midi.init()
        self.midi = pygame.midi.Input(3, 0)

        pygame.mixer.init()

        self.correctChord = self.getMajorChordSequence(whichChord) 

    def get_tones(self):
        if(self.midi.poll()):
            message = self.midi.read(3)
                       
            if len(message) == len(self.correctChord):
                chord = [message[0][0][1] , message[1][0][1], message[2][0][1]]
                if (self.matchChords(self.correctChord, chord)):
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
        for i in range(0,len(list2)):
            list2[i] = list2[i] % 12
        return sorted(list1) == sorted(list2)

if __name__=="__main__":

    piano = ToyPianoConsole(0)
    print "reading notes"
    while(1):
       piano.get_tones()
       time.sleep(1)


