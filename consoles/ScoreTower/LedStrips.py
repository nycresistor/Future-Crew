Ñò
.µQc           @   sR  d  d k  Z  d  d k Z d  d k Z d  d k Z d d d     YZ e d j oþe i   Z e i d d d d d	 d
 d d e i d d d d d	 d d d d e	 e i
   \ Z Z d Z e e d  Z e i e i  d Z d Z xbe oVd Z xe d e i  D]û Z xò e d e  D]á Z e e d d j o4 e e d  7Z e e d  7Z e e d  7Z n e e d d j o4 e e d  7Z e e d  7Z e e d  7Z n e e d d j o4 e e d  7Z e e d  7Z e e d  7Z q"q"WqWe d d Z e d j o e d d Z n e i e  qì Wn d S(   iÿÿÿÿNt	   LedStripsc           B   sJ   e  Z d  Z d  Z d   Z d   Z d   Z d   Z d   Z d   Z	 RS(   i    c         C   s   | |  _  | |  _ d S(   s`   
		Initialize an med strip
		@param offset X position of the image to get LED image data from
		N(   t   image_widtht   offset(   t   selfR   R   (    (    s.   /Users/holly/resistor/future-crew/LedStrips.pyt   __init__   s    	c         C   s   t  i | d d d |  _ d  S(   Ni Â t   timeouti    (   t   serialt   Serialt   ser(   R   t   port(    (    s.   /Users/holly/resistor/future-crew/LedStrips.pyt   connect   s    c         C   s°  t  |  d j o t d t  |    n d } t i d |  } | d 7} xl t d d d  D]X } d } x9 t d d	  D]( } | | d
 d | | ?d
 @| >7} q~ W| t |  7} qb W| d 7} xh t d d d  D]T } d } x5 t d d	  D]$ } | | d | | ?d
 @| >O} q÷ W| t |  7} qÛ W| d 7} xl t d d d  D]X } d } x9 t d d	  D]( } | | d d | | ?d
 @| >O} qlW| t |  7} qPW| S(   sé   
		Convert a row of eight RGB pixels into LED strip data.
		@param data 24-byte array of 8bit RGB data for one row of pixels:
			0  1  2  3  4  5  6  7
			RGBRGBRGBRGBRGBRGBRGBRGB
		@return 24-byte stream to write to the USB port.
		i   s!   Expected 24 bytes of data, got %it    t   Bs   ÿi   i    iÿÿÿÿi   i   i   i   (   t   lent	   Exceptiont   arrayt   ranget   chr(   R   t   datat   outputt	   bit_indext   ct   pixel_index(    (    s.   /Users/holly/resistor/future-crew/LedStrips.pyt   RgbRowToStrips   s:    
  &
  "
  &c         C   s   |  i  |  |  i   d S(   sh   
		Draw a portion of an image frame to LED strips.
		@param data Image data, as a 1D, 8bit RGB array.
		N(   t	   load_datat   flip(   R   R   (    (    s.   /Users/holly/resistor/future-crew/LedStrips.pyt   drawA   s    c         C   sS  d } d } x~ t  d t |  d |  i  D]\ } |  i | |  i d } t i   } | |  i | | | d ! 7} | t i   | 7} q- Wt i   } xJ t  d t |  d  D]/ } | d | d | d !}	 |  i i |	  q³ Wt i   | }
 |  i | 7_ |  i	 d 7_	 |  i	 d j o+ |  i |  i	 } d |  _	 d |  _ | GHn d S(	   s~   
		Load the next frame into the strips, but don't actually clock it out.
		@param data Image data, as a 1D, 8bit RGB array.
		R   i    i   i   i@   i   i   N(
   R   R   R   R   t   timeR   R   t   writet   format_time_totalt   frame_count(   R   R   t   st   format_timet   rowt   start_indext   format_start_timet   output_start_timet   xt   tt   output_timet   average_time(    (    s.   /Users/holly/resistor/future-crew/LedStrips.pyR   I   s*    !  		c         C   s.   x' t  d d  D] } |  i i d  q Wd  S(   Ni    i@   t    (   R   R   R   (   R   t   i(    (    s.   /Users/holly/resistor/future-crew/LedStrips.pyR   i   s     (
   t   __name__t
   __module__R   R   R   R
   R   R   R   R   (    (    (    s.   /Users/holly/resistor/future-crew/LedStrips.pyR       s   			*		 t   __main__s   -ps   --serialportt   destt   serial_portt   helps   serial port (ex: /dev/ttyUSB0)t   defaults   /dev/tty.usbmodel12341s   -ls   --lengtht   strip_lengths   length of the stripi    t   typei   i    R   i   iÿ   i   i   i   (    (   R   R   t   optparseR   R    R+   t   OptionParsert   parsert
   add_optiont   intt
   parse_argst   optionst   argsR   t   stripR
   R/   R*   t   jt   TrueR   R   R2   R!   t   colR   R   (    (    (    s.   /Users/holly/resistor/future-crew/LedStrips.pyt   <module>   sN   i   