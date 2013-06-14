import LedStrips
import optparse
import array
import time
import serial
import threading

console_map = {
        'ToyPianoClient':0,
        'PatchConsole':1,
        'VidEditConsole':2,
        'TeletypeConsole':3
}

def match_console(console):
	try:
                return console_map[console]
        except:
                return 0

#globals
running = False
mode = None
queue = []
queueLock = threading.RLock()

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

attract_j = 0
def attract():
        "Make a lovely wave pattern"
        global attract_j
        global mode
	if not strip:
		return
        patt_len = len(attract_pattern)/3
	#j = 0 				# flow in
        mode = 'attract'
        class AttractThread(threading.Thread):
                def run(self):
                        global mode
                        global attract_j
                        while mode == 'attract':
                                start = (attract_j % patt_len)*image_width*3
                                bytelen = strip_length*image_width*3
                                strip.draw(compiled_attract[start:bytelen+start])
                                attract_j -= 1 	# flow out
                                if attract_j == -1:
                                        attract_j += patt_len
                                time.sleep(0.04)
        at = AttractThread()
        at.start()

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
	# retain the score bar
	for row in range(0, score)
		for col in range( 0, image_width):
			data += chr(75)	
			data += chr(75)	
			data += chr(75)	
	# above the score tower, blink the console with the miss
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


# Make strip blink white if console sends a hit
#def hit():
def game_hit(console, score):
	if not strip:
		return
	console = match_console(console)
	score = score + 20
        data = ''
	# retain the score bar
	for row in range(0, score)
		for col in range( 0, image_width):
			data += chr(75)	
			data += chr(75)	
			data += chr(75)	
	# above the score bar, blink the console with the hit
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
				data += chr(0)
				data += chr(0)
				data += chr(0)

		strip.draw(data)
		time.sleep(.3)
		k = k + 1

	queue_attract()

# Make all strips blink white if servers declare game is won
def session_won():
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
				data += chr(0)
				data += chr(0)
				data += chr(0)

		strip.draw(data)
		time.sleep(.3)
		k = k + 1
                
	queue_attract() 	# Return to idle/attract mode

strip_length = 160
strip = None
image_width = 8 # width of the picture

lightThread = None

class TowerThread(threading.Thread):
        def run(self):
                global queue
                global queueLock
                global running
                global mode
                running = True
                print "Thread starting"
                while (running):
                        while queue:
                                mode = None
                                queueLock.acquire()
                                if queue:
                                        m = queue.pop(0)
                                        m()
                                queueLock.release()
                        time.sleep(0.05)

                        
# public functions below

def queue_attract():
        queueLock.acquire()
        queue.append(attract)
        queueLock.release()

def queue_session_begin():
        queueLock.acquire()
        queue.append(session_begin)
        queueLock.release()

def queue_session_won():
        queueLock.acquire()
        queue.append(session_won)
        queueLock.release()

def queue_session_lost():
        queueLock.acquire()
        queue.append(session_lost)
        queueLock.release()

def queue_game_hit(console,score):
        queueLock.acquire()
        queue.append(lambda:game_hit(console,score))
        queueLock.release()

def queue_game_miss(console,score):
        queueLock.acquire()
        queue.append(lambda:game_miss(console,score))
        queueLock.release()

def stop():
        global queue
        global mode
        global running
        queue = []
        mode = None
        running = False

def init(serialport):
	global strip
	strip=LedStrips.LedStrips(image_width,0)
	strip.connect(serialport)
	print "Initialized strip"
        TowerThread().start() 

def shutdown():
        stop()
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
                queue_attract()
                time.sleep(4)
                queue_game_hit('VidEditConsole',5);
                time.sleep(2)
                queue_game_miss('VidEditConsole',-5);
                time.sleep(2)
                queue_game_hit('VidEditConsole',5);
                queue_game_miss('VidEditConsole',-5);
                time.sleep(2)
                shutdown()
        finally:
                shutdown()

