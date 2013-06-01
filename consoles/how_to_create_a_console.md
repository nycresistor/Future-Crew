


How to create a Future Crew console
===================================

System requirements
-------------------
Future Crew consoles need to have some sort of decent computer backing it; if you're implementing your console with Teensies or Arduinos they'll need to connect to a Raspberry Pi or other machine to act as the actual FC node. We have several RPis set aside for Future Crew use.

Ask for help setting up a Raspberry Pi image if you need it. While developing your console, you may want to use your laptop or whatever until you're ready to install it on a Pi.

Here's what you'll need for a node:

- Python 2.6 or thereabouts
- Python websocket-client package. There are many python websocket 
  packages, so make sure to install the correct one:
  - pip install websocket-client
- Python serial package (pyserial).
  - On debian: apt-get install python-serial
  - On openembedded: opkg install python-serial
- Local network connection

What the hell is a console
--------------------------

A console consists of two basic parts:
- The "game" component, which is a set of switches, dials, plugs, etc. that the player has to manipulate to complete a task
- The "message" component, which is a display terminal or other device capable of displaying ASCII text

