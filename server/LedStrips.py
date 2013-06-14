import serial
import time
import optparse
import array

class LedStrips:

	frame_count = 0
	format_time_total = 0


	def __init__(self, image_width, offset):
		"""
		Initialize an med strip
		@param offset X position of the image to get LED image data from
		"""
		self.image_width = image_width
		self.offset = offset

	def connect(self, port):
		self.ser = serial.Serial(port, 115200, timeout=0)

	def RgbRowToStrips(self, data):
		"""
		Convert a row of eight RGB pixels into LED strip data.
		@param data 24-byte array of 8bit RGB data for one row of pixels:
			0  1  2  3  4  5  6  7
			RGBRGBRGBRGBRGBRGBRGBRGB
		@return 24-byte stream to write to the USB port.
		"""
		if len(data) != 24:
			raise Exception('Expected 24 bytes of data, got %i'%(len(data)))

		output = ''

		data = array.array('B', data)

		# Green byte
		output += '\xFF'
		for bit_index in range(7, 0, -1):
			c = 0x00
			for pixel_index in range(0, 8):
				c += (data[1+3*pixel_index] >> bit_index & 1) << pixel_index
			output += chr(c)

		# Red byte
		output += '\xFF'
		for bit_index in range(7, 0, -1):
			c = 0x00
			for pixel_index in range(0, 8):
				c |= (data[3*pixel_index] >> bit_index & 1) << pixel_index
			output += chr(c)

		# Blue byte
		output += '\xFF'
		for bit_index in range(7, 0, -1):
			c = 0x00
			for pixel_index in range(0, 8):
				c |= (data[2+3*pixel_index] >> bit_index & 1) << pixel_index
			output += chr(c)


		return output

	def draw(self, data):
		"""
		Draw a portion of an image frame to LED strips.
		@param data Image data, as a 1D, 8bit RGB array.
		"""
		self.load_data(data)
		self.flip()

        def compile(self, data):
		# for each 'row' in the data, assemble a byte stream for it.
                s = ''
		for row in range(0,len(data)/3/self.image_width):
			start_index = (self.image_width*row + self.offset)*3
			s += self.RgbRowToStrips(data[start_index:start_index+24])
                return s
        
        def fast_draw(self, data):
		for x in range(0, len(data)/64):
			t = data[64 * x : (64 * x) + 64]
			self.ser.write(t)

	def load_data(self, data):
		"""
		Load the next frame into the strips, but don't actually clock it out.
		@param data Image data, as a 1D, 8bit RGB array.
		"""

		s = ''

		format_time = 0
		# for each 'row' in the data, assemble a byte stream for it.
		for row in range(0,len(data)/3/self.image_width):
			start_index = (self.image_width*row + self.offset)*3
			format_start_time = time.time()
			s += self.RgbRowToStrips(data[start_index:start_index+24])
			format_time += time.time() - format_start_time

		# Send the data out in 64-byte chunks
		output_start_time = time.time()
		for x in range(0, len(s)/64):
			t = s[64 * x : (64 * x) + 64]
			self.ser.write(t)
                # Turn off 'profiling' for now
                if False:
                        output_time = time.time() - output_start_time

                        self.format_time_total += format_time
                        self.frame_count += 1

                        if self.frame_count > 30:
                                average_time = self.format_time_total/self.frame_count
                                self.frame_count = 0
                                self.format_time_total = 0
                                print average_time

	def flip(self):
		# TODO: Why does 20 work? it make a'no sense.
                # 1 does not work with the listener.
		for i in range(0,64):
			self.ser.write('\x00')

if __name__ == "__main__":
	parser = optparse.OptionParser()
	parser.add_option("-p", "--serialport", dest="serial_port",
		help="serial port (ex: /dev/ttyUSB0)", default="/dev/tty.usbmodel12341")
	parser.add_option("-l", "--length", dest="strip_length",
		help="length of the strip", default=160, type=int)

	(options, args) = parser.parse_args()

        image_width = 8 # width of the picture

	strip = LedStrips(image_width, 0)
        strip.connect(options.serial_port)

	i = 0
	j = 0
	while True:
		data = ''
		for row in range(0, options.strip_length):
			for col in range(0, image_width):
				if ((row+j)%3 == 0):
					data += chr(255) # R
					data += chr(0) # G
					data += chr(0) # B
				if ((row+j)%3 == 1):
					data += chr(0) # R
					data += chr(0) # G
					data += chr(0) # B
				if ((row+j)%3 == 2):
					data += chr(0) # R
					data += chr(0) # G
					data += chr(255) # B
#				data += chr(0xFF) # B
#				data += chr(0xFF) # B
#				data += chr(0xFF) # B

		i = (i+1)%20
                if i == 0:
			j = (j+1)%255


	        strip.draw(data)
