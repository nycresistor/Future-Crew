import LedStrips
import optparse
import array
import time
import serial

def match_console(console):
	if console == 'ToyPianoClient':
		console = 0
	if console == 'PatchConsole':
		console = 1
	if console == 'VidEditConsole':
		console = 2
	if console == 'TeletypeConsole':
		console = 3

	return console

######################################################
#### Strip pattern control functions (\/ below \/) ###

#color_black = chr(0) + chr(0) + chr(0)
#color_light_blue = chr(0) + chr(5) + chr(0)

# Make a lovely wave pattern 
def attract():
	if not strip:
		return
	i = 0
	#j = 0 				# flow in
	j = strip_length 	# flow out
	k = 0
	while True:
        	data = ''
        	for row in range(0, strip_length):
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
                	#j = (j+1)%255  # flow in
                	j = (j-1)%255 	# flow out
			if j == -1:
				j = strip_length
	
        	strip.draw(data)
				

# When a session starts, make a scorebar
def scoretower_begin():
	if not strip:
		print "no strip available"
		return
	# A score of '0' will be indicated by a bar of 20 LED pixels
	# it will go up or down as the score changes
	score = 20
	data = ''
	for row in range(0, score):
		for col in range(0, image_width):
			data += chr(75)	
			data += chr(75)	
			data += chr(75)	
	for row in range(score+1, strip_length):
		for col in range(0, image_width):
			data += chr(0)	
			data += chr(0)	
			data += chr(0)	
			
       	strip.draw(data)

# Make strip blink red if consoles sends a miss
def scoretower_miss(console, score):
	if not strip:
		return
	console = match_console(console)
	score = score + 20
        data = ''
        for row in range(score, strip_length):
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
        time.sleep(.2)
	# Update score tower
	data = ''
	for row in range(0, score):
		for col in range(0, image_width):
			data += chr(75)	
			data += chr(75)	
			data += chr(75)	
	for row in range(score, strip_length):
		for col in range(0, image_width):
			data += chr(0)	
			data += chr(0)	
			data += chr(0)	
        strip.draw(data)


# Make strip blink white if consoles sends a hit
#def hit():
def scoretower_hit(console, score):
	if not strip:
		return
	console = match_console(console)
	score = score + 20
        data = ''
        for row in range(score, strip_length):
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
        time.sleep(.2)
	# Update score tower
	data = ''
	for row in range(0, score):
		for col in range(0, image_width):
			data += chr(75)	
			data += chr(75)	
			data += chr(75)	
	for row in range(score, strip_length):
		for col in range(0, image_width):
			data += chr(0)	
			data += chr(0)	
			data += chr(0)	
        strip.draw(data)


# Make all strips blink red if servers declares game is lost
def scoretower_lost():
	if not strip:
		return
	k = 0
	while k < 6:
		data = ''
		for row in range(0, strip_length):
			for col in range(0, image_width):
				data += chr(255)
				data += chr(0)
				data += chr(0)

		strip.draw(data)
		time.sleep(.3)

		data = ''
		for row in range(0, strip_length):
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
def scoretower_won():
	if not strip:
		return
	k = 0
	while k < 6: 	# blink 5 times
		data = ''
		for row in range(0, strip_length):
			for col in range(0, image_width):
				# blink on
				data += chr(75)
				data += chr(75)
				data += chr(75)

		strip.draw(data)
		time.sleep(.3)

		data = ''
		for row in range(0, strip_length):
			for col in range(0, image_width):
				# blink off
				print col
				data += chr(0)
				data += chr(0)
				data += chr(0)

		strip.draw(data)
		time.sleep(.3)
		k = k + 1

	attract() 	# Return to idle/attract mode

strip_length = 160
strip = None
image_width = 8 # width of the picture

def init(serialport):
	global strip
	strip=LedStrips.LedStrips(image_width,0)
	strip.connect(serialport)
	print "Initialized strip"

#### Strip pattern control functions (/\ above /\) ###
######################################################

if __name__ == "__main__":
	parser = optparse.OptionParser()
	parser.add_option("-p", "--serialport", dest="serial_port",
		help="serial port (ex: /dev/ttyUSB0)", default="/dev/tty.usbmodel12341")
	parser.add_option("-l", "--length", dest="strip_length",
        	help="length of the strip", default=160, type=int)
	
	(options, args) = parser.parse_args()
	strip_length = options.strip_length
	init(options.serial_port)



