<pre>
 ___________________
( Toy Piano Console )
 -------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
</pre>

It's the toy piano that Shelby found in the street, wired up so 
each of its keys can transmit either a keyboard press or
a MIDI note. See teensyduino code for key mapping.

So far, it can only send keypresses.  It has no lights, meters, etc. 

futurecrew_toypiano is the teensyduino sketch.  It requires the bounce library
from http://playground.arduino.cc/code/bounce

toypiano.py is the console controller.  Run it with
`PYTHONPATH=.. python toypiano.pi`

feedback sounds in ogg format are in sounds/ folder.  I found some useable placeholder sounds already oggified at http://www.acoustica.com/files/aclooplib/ especially http://www.acoustica.com/files/aclooplib/Sound%20Effects%20Tones/

Installation
============

Install the ToyPianoConsole (game) script:
  sudo cp ToyPianoConsole.init.d /etc/init.d/ToyPianoConsole
  sudo update-rc.d ToyPianoConsole defaults 99

Reboot:
  sudo reboot

