import LedStrips
import optparse
import array
import time
import serial

### Console Names:
# ToyPianoClient
# PatchConsole
# VidEditConsole

######################################################
#### Strip pattern control functions (\/ below \/) ###

#color_black = chr(0) + chr(0) + chr(0)
#color_light_blue = chr(0) + chr(5) + chr(0)

# Make a lovely wave pattern 
def attract():
	i = 0
	j = options.strip_length
	k = 0
	while True:
        	data = ''
        	for row in range(0, options.strip_length):
                	for col in range(0, image_width):
				# Every third one should be a diff color
			#black
                        	if ((row+j)%15 == 0):
                                	data += chr(0) # R
                                	data += chr(0) # G
                                	data += chr(0) # B
			#light blue
                        	if ((row+j)%15 == 1):
                                	data += chr(0) # R
                                	data += chr(5) # G
                                	data += chr(0) # B
			#light blue
                        	if ((row+j)%15 == 2):
                                	data += chr(0) # R
                                	data += chr(10) # G
                                	data += chr(5) # B
			#light blue
                        	if ((row+j)%15 == 3):
                                	data += chr(5) # R
                                	data += chr(20) # G
                                	data += chr(5) # B
			#blue
                        	if ((row+j)%15 == 4):
                                	data += chr(10) # R
                                	data += chr(50) # G
                                	data += chr(5) # B
			#light white
                        	if ((row+j)%15 == 5):
                                	data += chr(10) # R
                                	data += chr(60) # G
                                	data += chr(10) # B
			#light white
                        	if ((row+j)%15 == 6):
                                	data += chr(20) # R
                                	data += chr(80) # G
                                	data += chr(20) # B
			#light white
                        	if ((row+j)%15 == 7):
                                	data += chr(20) # R
                                	data += chr(100) # G
                                	data += chr(60) # B
			#white
                        	if ((row+j)%15 == 8):
                                	data += chr(50) # R
                                	data += chr(150) # G
                                	data += chr(100) # B
			#light white
                        	if ((row+j)%15 == 9):
                                	data += chr(20) # R
                                	data += chr(100) # G
                                	data += chr(60) # B
			#light white
                        	if ((row+j)%15 == 10):
                                	data += chr(20) # R
                                	data += chr(80) # G
                                	data += chr(20) # B
			#light white
                        	if ((row+j)%15 == 11):
                                	data += chr(10) # R
                                	data += chr(60) # G
                                	data += chr(10) # B
			#blue
                        	if ((row+j)%15 == 12):
                                	data += chr(10) # R
                                	data += chr(50) # G
                                	data += chr(5) # B
			#light blue
                        	if ((row+j)%15 == 13):
                                	data += chr(5) # R
                                	data += chr(20) # G
                                	data += chr(5) # B
			#light blue
                        	if ((row+j)%15 == 14):
                                	data += chr(0) # R
                                	data += chr(10) # G
                                	data += chr(5) # B
			#light blue
                        	if ((row+j)%15 == 15):
                                	data += chr(0) # R
                                	data += chr(5) # G
                                	data += chr(0) # B
			#black
                        	if ((row+j)%15 == 16):
                                	data += chr(0) # R
                                	data += chr(0) # G
                                	data += chr(0) # B
        	#i = (i+1)%20
        	i = (i+1)%2
		# increment j after 20 iterations
        	if i == 0:
			# count from 0 to 255, and do it again
                	#j = (j+1)%255
                	j = (j-1)%255
			if j == -1:
				j = options.strip_length
	
        	strip.draw(data)
				

# Make the column white mid-way up at the start of the game
#def play_mode():

# Make strip blink red if consoles sends a miss
def miss(console):
        data = ''
        for row in range(0, options.strip_length):
                for col in range(0, image_width):
                        if col == console:
                                data += chr(255)
                                data += chr(0)
                                data += chr(0)
                        else:
                                data += chr(0)
                                data += chr(0)
                                data += chr(0)

        strip.draw(data)
        # Wait.
        time.sleep(.5)

# Make strip blink white if consoles sends a hit
#def hit():
def hit(console):
        data = ''
        for row in range(0, options.strip_length):
                for col in range(0, image_width):
                        if col == console:
                                data += chr(255)
                                data += chr(255)
                                data += chr(255)
                        else:
                                data += chr(0)
                                data += chr(0)
                                data += chr(0)

        strip.draw(data)
        # Wait.
        time.sleep(.5)

# Make all strips blink red if servers declares game is lost
def lost():
	k = 0
	while k < 6:
		data = ''
		for row in range(0, options.strip_length):
			for col in range(0, image_width):
				data += chr(255)
				data += chr(0)
				data += chr(0)

		strip.draw(data)
		time.sleep(.3)

		data = ''
		for row in range(0, options.strip_length):
			for col in range(0, image_width):
				print col
				data += chr(0)
				data += chr(0)
				data += chr(0)

		strip.draw(data)
		time.sleep(.3)
		k = k + 1

	attract()

# Make all strips blink white if servers declare game is won
def won():
	k = 0
	while k < 6:
		data = ''
		for row in range(0, options.strip_length):
			for col in range(0, image_width):
				data += chr(75)
				data += chr(75)
				data += chr(75)

		strip.draw(data)
		time.sleep(.3)

		data = ''
		for row in range(0, options.strip_length):
			for col in range(0, image_width):
				print col
				data += chr(0)
				data += chr(0)
				data += chr(0)

		strip.draw(data)
		time.sleep(.3)
		k = k + 1

	attract()

#def play_mode():
	
	

#### Strip pattern control functions (/\ above /\) ###
######################################################

parser = optparse.OptionParser()
parser.add_option("-p", "--serialport", dest="serial_port",
	help="serial port (ex: /dev/ttyUSB0)", default="/dev/tty.usbmodel12341")
parser.add_option("-l", "--length", dest="strip_length",
        help="length of the strip", default=160, type=int)

(options, args) = parser.parse_args()

image_width = 8 # width of the picture

strip = LedStrips.LedStrips(image_width, 0)
strip.connect(options.serial_port)

won()
#lost()
#miss(1)
#attract()


