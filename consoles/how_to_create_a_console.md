


How to create a Future Crew console
===================================

System requirements
-------------------
Future Crew node need to run on sort of basic computer; if you're implementing your console with Teensies or Arduinos they'll need to connect to a Raspberry Pi or other machine to act as the actual FC node. We have several RPis set aside for Future Crew use.

Ask for help setting up a Raspberry Pi image if you need it. While developing your console, you may want to use your laptop or whatever until you're ready to install it on a Pi.

Here's what you'll need for a node:

- Python 2.6 or thereabouts
- Python websocket-client package. There are many python websocket 
  packages, so make sure to install the correct one:
  - pip install websocket-client
- If you're using serial connections to connect to your microcontrollers, you'll need the python serial package (pyserial).
  - On debian: apt-get install python-serial
  - On openembedded: opkg install python-serial
- Local network connection
- The files in this repository

Configuring Pi's
----------------
For Raspbian wheezy and likely other distributions, you will need to
setup tornado and other dependencies:

    sudo apt-get update # get a coffee...
    sudo apt-get upgrade # Fly to Brazil to harvest a coffee crop
    sudo apt-get install python-pip python2.7-dev
    sudo apt-get install libevent-dev
    sudo pip install tornado
    sudo pip install websocket-client

Console hardware
----------------

A console consists of two basic parts:
- The "game" component, which is a set of switches, dials, plugs, etc. that the player has to manipulate to complete a task
- The "message" component, which is a display terminal or other device capable of displaying ASCII text

You should be able to communicate with both of these components from your node.

Games and Message Slots
-----------------------

A "game" in the context of Future Crew is a simple task that can be performed at a console. For instance, a game could be:
* Push all the blinking buttons
* Plug port A into port 7
* Turn dial X to 500
* Play "Ode to Joy" on a toy piano
Games can be as complex or simple as you like; it's up to the node to implement them. The only restrictions that a game needs to have are:
* The task needs to be described (in a goofy or simple way) in under 80 characters of text
* It should be able to be accomplished fairly quickly
* The console should be able to report success or failure

A "message slot" is a area of the message component where a text message can be displayed. A console can have zero or more message slots. (A console could be composed entirely of message slots and have no games-- the player would just shout out instructions for other people! This could be used for a fast food restaurant simulator.) A message is displayed on a message slot until the server sends another message to replace it (or clears it).

Outline of a console implementation
-----------------------------------

The "future_client" python package provides the three classes you'll need to use to create a console: FutureClient, Game, and MessageSlot. You'll need to make sure he future_client.py file is in your PYTHON_PATH; you can do this either by copying or linking the file into a directory in your python path (not recommended) or by adding the directory it's in to the PYTHON_PATH variable at runtime. For instance, when I run the curses client from the TestClients directory, I invoke it like this:
```bash
PYTHON_PATH=.. python curses_client.py
```

You implement the console in python. You'll want to start out by importing the important bits of the interface, like so:
```python
from future_client import FutureClient, Game, MessageSlot
```
You'll subclass the "Game" object to implement games, and the "MessageSlot" object to implement message slots. You generally won't need to subclass FutureClient.

Creating a game
---------------
*This section will probably change-- I will move the threading code into the client so the user doesn't have to do threading.*

Creating a message slot
-----------------------

Creating a message slot is similar: you just need to subclass a MessageSlot class and override the on_message() function. Here's an example message slot that just prints out the messages sent to it:

```python
class SimpleMessageSlot(MessageSlot):
    def __init__(self, slotname):
        self.slotname = slotname
        super(SimpleMessageSlot,self).__init__()
    def on_message(self,text):
        if text:
            print "Simple Slot",self.slotname,"says:",text
        else:
            print "Simple Slot",self.slotname,"has been cleared!"
```
