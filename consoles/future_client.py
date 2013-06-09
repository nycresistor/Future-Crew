from websocket import create_connection, socket
import json
import time
import threading
from os import getenv

class RegistrationError(Exception):
    pass

def next_id():
    '''Convenience for autogenerating IDs for lazy programmers'''
    id = next_id.nid
    next_id.nid += 1
    return id
next_id.nid = 0

class MessageSlot(object):
    '''A text display for a message from the server. Each must have a console-unique id.'''
    def __init__(self,id=None,length = 40):
        if id == None:
            id = next_id()
        self.id = id
        self.length = length
        self.in_use = False
        self.text = None
    def message(self,text):
        self.in_use = bool(text)
        self.text = text
        self.on_message(text)

    def on_message(self,text):
        print "MESSAGE: ",text

    def jsonable(self):
        return {
            'id':self.id,
            'len':self.length
            }

class Game(object):
    '''
    A Game object represents a game that is played on the console.

    All you need to do to create a game is subclass Game and implement
    the play_game method. Games always run in their own threads.

    During the play_game method, you should check the self.running variable.
    If it has been set to False, it means that the game has been cancelled
    and the method should exit as quickly as possible.
    '''

    def __init__(self, gameid, message):
        '''Create a game object. Games must have unique game ids as well
        as an initial message string. Games can change the displayed string
        after they start running.'''
        self.id = gameid
        self.thread = None
        self.score = None
        self.start_time = 0
        self.message = message
        self.exit_evt = threading.Event()
        self.exit_evt.set()

    def start(self,client):
        self.client = client
        self.start_time = time.time()
        t = threading.Thread(target = self.play_game_wrapper)
        self.thread = t
        t.start()

    def play_game_wrapper(self):
        self.exit_evt.clear()
        self.score = None
        self.play_game()
        self.exit_evt.set()
        if self.score == None:
            self.score = 0
        won = self.score > 0
        msg = { 'a':'update',
                'gameid': self.id,
                'running': False,
                'result': won,
                'score': self.score
                }
        self.client.socket.send(json.dumps(msg))

    def wait(self,how_long):
        return not self.exit_evt.wait(how_long)

    def is_running(self):
        return not self.exit_evt.is_set()

    def cancel(self):
        self.finish(0)

    def finish(self,score):
        if self.score == None:
            self.score = score
        self.exit_evt.set()

    def play_game(self):
        '''
        play_game should check self.is_running() to make sure it exits
        quickly once the game has been cancelled. Make sure
        your game eventually ends!

        If you need to wait for an set amount of time to pass while
        the game is running, use the self.wait() method instead
        of time.sleep() or similar functions. self.wait() will immediately
        return when the game is cancelled. It will also return True if the
        game is still running, or False if it has been cancelled.

        play_game should call self.finish(score) and return when the game
        is completed (one way or the other). Calling finish multiple times
        will result in the first indicated score being used. If finish is
        not called before the game ends, the score will be assumed to be
        0 (a loss).
        '''
        raise Exception("play_game must be implemented!")

    def jsonable(self):
        d = { 'message':self.message,
              'gameid':self.id,
              'level':0,
              'time':0 }
        return d

    def update_message(self, new_msg):
        msg = { 'a':'update',
                'gameid': self.id,
                'running': True,
                'message': new_msg
                }
        self.client.socket.send(json.dumps(msg))

class FutureClient(object):
    """A FutureClient is a forward-thinking class ready to take on
    the risks and responsibilities that the future offers. Are you
    ready to extend FutureClient?"""
    
    def __init__(self,urlstring = None,name='Generic Client',max_games=1):
        if not urlstring:
            urlstring = getenv('SERVER_URL',"ws://localhost:2600/socket")
        self.name = name
        self.socket = None
        while (self.socket == None):
            try:
                self.socket = create_connection(urlstring,5.0)
            except socket.error:
                print "Could not connect to server. Trying again."
                time.sleep(1.5)

        self.running_games = set()
        msg = {'a':'register','name':self.name}
        self.socket.send(json.dumps(msg))
        self.message_slots = set()
        self.available_games = set()
        self.max_games = max_games
        self.cmdmap = {
            'message': self.on_message,
            'control': self.on_control
            }
        self.started = False
        self.Thread = None

    def on_message(self, msg):
        slotid = msg['slotid']
        slot = next(s for s in self.message_slots if s.id == slotid)
        slot.message(msg['text'])

    def on_control(self, msg):
        gameid = msg['game']['gameid']
        game = next(g for g in self.available_games if g.id == gameid)
        if msg['operation'] == 'start':
            game.start(self)
        elif msg['operation'] == 'cancel':
            game.cancel()

    def status(self):
        self.running_games = [x.jsonable() for x in self.available_games if x.is_running()]
        msg = {
            'a':'status',
            'avail_slots':[x.jsonable() for x in self.message_slots if not x.in_use],
            'avail_games':[x.jsonable() for x in self.available_games if not x.is_running()],
            'bored':len(self.running_games) == 0
            }
        if self.max_games <= len(self.running_games):
            msg['avail_games'] = []
        self.socket.send(json.dumps(msg))

    def poll(self,timeout=-1):
        if timeout != -1:
            self.socket.settimeout(timeout)
        try:
            msgs = self.socket.recv()
            if msgs:
                msg = json.loads(msgs)
                self.cmdmap[msg['a']](msg)
        except socket.timeout:
            pass

    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        return self.thread

    def run(self):
        self.socket.settimeout(0.1)
        self.started = True
        while self.started:
            self.poll()
            self.status()

    def stop(self):
        self.started = False

    def quit(self):
        # abort all games
        for game in self.available_games:
            game.cancel()
        self.stop()
        if self.thread:
            self.thread.join()
        self.socket.close()

