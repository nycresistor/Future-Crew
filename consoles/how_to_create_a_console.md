


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

To create a game, just subclass the "Game" class and override the play_game() method. Here's a very, very simple game:
```python
class DeptOfMotorVehicles(Game):
    def __init__(self):
        super(DeptOfMotorVehicles, self).__init__(
            'DMV','Please take a seat.')

    def play_game(self):
        self.wait(60*60*4)
```

When this game starts, it will do nothing but wait for four hours. Once the game is over, the player is assumed to have lost. It's not a very fun game, but neither is the real DMV. You'll notice that we used the call self.wait() instead of time.delay() or whatever. You should always use self.wait() to delay; that's because it will immediately exit if the game is cancelled at any time.

You'll notice also that we've created a custom constructor here. It calls the parent constructor, which takes two arguments: the name of the game, and the message that should be sent to a console when the game starts.

Obviously, we want to be able to win games once in a while. Here's a slightly less pointless one:

```python
class FlipTheSwitch(Game):
    def __init__(self, whichSwitch):
        self.switch = whichSwitch 
        super(FlipTheSwitch, self).__init__(
            'FlipSwitch','Please flip switch '+whichSwitch)

    def play_game(self):
        starttime = time.time()
        while self.is_running() and (time.time() - starttime) < 10.0:
            self.wait(0.1):
            if flipped_switch(self.switch):
                self.finish(2)
```

This game will wait ten seconds for the user to flip the switch. If they do, it awards them two points using the self.finish() call. self.finish() sets the number of points earned for this game-- a positive number of points is a "win"; zero or fewer points is a "loss".

self.is_running() returns false if the game has been cancelled or 'finished', so it will return false after self.finish() is called. Thus, the game ends right after the user flips the switch.

self.wait() happens to return the value of self.is_running(), so we could make this even simpler:
```python
    def play_game(self):
        starttime = time.time()
        while self.wait(0.1) and (time.time() - starttime) < 10.0:
            if flipped_switch():
                self.finish(2)
```

That's about all there is to creating a game! Go crazy. There are a few things to know before you go too crazy, though:
* every game runs in its own thread. Be careful if you have code outside of play_game interacting with the variables in play_game!
* make sure play_game will always terminate quickly when it is cancelled! Otherwise your console may end up in a bad place.
* later, you'll see how to set the default message that is sent to a console when the game starts. However, you're not stuck with it forever-- you can send out updates while the game is running! Just use the self.update_message() call, like so:
```python
   self.update_message('Time is running out! Flip switch now!')
```

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

That's it!

Creating a client
-----------------

We're almost there! All we have to do is create a client object and tell it about the message slots and games available. Here's a quick example:

```python
    fc = FutureClient('ws://localhost:8888/socket','switchflipper')
    fc.available_games = [
        FlipTheSwitch('A'),
        FlipTheSwitch('B')
    ]
    fc.message_slots = [
        SimpleMessageSlot()
    ]
    fc.start()
    try:
        while True:
            time.sleep(1)
    except:
        pass
    fc.quit()
```

The FutureClient() initializer takes two arguments: the websocket URL of the server, and the name of the console. When fc.start() is called, the client starts. Since the client runs in its own thread, fc.start() returns immediately. You can then go into an infinite loop (as we do here), or do any task that your console requires (like checking for button presses).

And that's it! Your console is ready to go. Pester me when you run into the inevitable problems!

