import LedStrips
import optparse
import array
import time
import serial

console_map = {
        'ToyPianoClient':0,
        'PatchConsole':1,
        'VidEditConsole':2,
        'TeletypeConsole':3
}

def match_console(console):
	return console_map[console]

running = False

######################################################
#### Strip pattern control functions (\/ below \/) ###

#color_black = chr(0) + chr(0) + chr(0)
#color_light_blue = chr(0) + chr(5) + chr(0)

attract_pattern = [
        0,0,0,       #black
        0,5,0,       #light blue
        0,10,5,      #light blue
        5,20,5,      #light blue
        10,50,5,     #blue
        10,60,10,    #light white
        20,80,20,    #light white
        20,100,60,   #light white
        50,150,100,  #white
        20,100,60,   #light white
        20,80,20,    #light white
        10,60,10,    #light white
        10,50,5,     #blue
        5,20,5,      #light blue
        0,10,5,      #light blue
#        0,5,0,       #light blue
#        0,0,0,       #black
]

# intialize 'compiled' attract pattern
compiled_attract = []
for row in range(0, 160 + len(attract_pattern)/3):
        for col in range(0, 8):
                start = (row%(len(attract_pattern)/3))*3
                compiled_attract += attract_pattern[start:start+3]
compiled_attract=array.array('B',compiled_attract)

def stop():
        running = False

def attract():
        "Make a lovely wave pattern"
	if not strip:
		return
        patt_len = len(attract_pattern)/3
	#j = 0 				# flow in
	j = patt_len 	# flow out
	k = 0
        running = True
	while running:
                start = (j % patt_len)*image_width*3
                bytelen = strip_length*image_width*3
                strip.draw(compiled_attract[start:bytelen+start])
                j -= 1 	# flow out
                if j == -1:
                        j += patt_len
                time.sleep(0.04)
				

# When a session starts, make a scorebar
def session_begin():
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
def game_miss(console, score):
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
def game_hit(console, score):
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
def session_lost():
	if not strip:
		return
	k = 0
        running = True
	while running and k < 6:
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
def session_won():
	if not strip:
		return
	k = 0
        running = True
	while running and k < 6: 	# blink 5 times
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

def shutdown():
        if strip:
                strip.draw([0]*(strip_length*image_width*3))

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
        try:
                game_miss('VidEditConsole',10)
                #session_lost()
                attract()
        finally:
                shutdown()

