<pre>
 _______________________
( Video Editing Console )
 -----------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
</pre>

drawing.png has a guide to all the various switches and levers on the console.

panel_teensy is the teensy2.0 sketch for the electronics driving the console.

Panel Protocol
==============

Commands consist of one byte and then a variable-length payload.

0x00 - reserved

0x01 - set LED. Followed by a one-byte index, and then a one-byte mode. (See below for modes.)

0x02 - set illuminated switch. Followed by a one-byte index, and then a one-byte mode. (See below for modes.)

0x03 - read illuminated switches. Returns a four-byte bitmap in big-endian order with 1s representing currently pressed switches.

0x04 - read non-illuminated buttons. Returns a five-byte bitmap in big-endian order with 1s representing currently pressed switches.

0x05 - read pushswitches. NYD.

0x06 - read encoders. NYD.
