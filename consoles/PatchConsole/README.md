 ____       _       _     ____                  _ 
|  _ \ __ _| |_ ___| |__ |  _ \ __ _ _ __   ___| |
| |_) / _` | __/ __| '_ \| |_) / _` | '_ \ / _ \ |
|  __/ (_| | || (__| | | |  __/ (_| | | | |  __/ |
|_|   \__,_|\__\___|_| |_|_|   \__,_|_| |_|\___|_|

The patch panel console has 35 BNC connectors that can be
"patched" with cables and eight switches that can be toggled.
The firmware determines which ports are connected to which other
ports and prints on the serial port messages of the form:

[switches] [from:to] [from:to]...

Sample output with four switches set and three cables plugged in:

17 A7:B2 B6:F7 F4:F5

The switches are an 8-bit bitmap.  The names of the ports correspond
to the IO port on the Teensy++ that is used.  The front panel should
have its names redone to be funnier.


The games are:

Activate [switch x]!
Disable [switch x]!
Wiggle [switch x]! (meaning toggle it, and then toggle it back)

[verb] [input] to [other input]!
	Patch, connect, route, reroute, wire, introduce, bridge, hook up,
	plug, span, affix

[verb] [input]!
	Sever, disconnect, pull the plug on, disable, eliminate,
	separate, bisect

Disconncted all patches!

Installation
============

Install the invasion (display) script:
  sudo cp invasion.init.d /etc/init.d/invasion
  sudo update-rc.d invasion defaults 99

Install the PatchConsole (game) script:
  sudo cp PatchConsole.init.d /etc/init.d/PatchConsole
  sudo update-rc.d PatchConsole defaults 99

Reboot:
  sudo reboot
A
A
A
A
A
A
A
A
A
A


