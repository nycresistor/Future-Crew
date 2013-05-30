from websocket import create_connection, socket
import json
import time
import threading

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
    def __init__(self, gameid, message, level =-1, time =-1):
        self.id = gameid
        self.running = False
        self.message = message
        self.time = time
        self.level = level

    def start(self,client):
        self.client = client
        self.start_time = time.time()
        self.running = True
        self.on_start()

    def cancel(self):
        self.running = False
        self.on_cancel()

    def on_start(self):
        print "Game {0} started!".format(self.id)

    def on_cancel(self):
        print "Game {0} cancelled!".format(self.id)

    def is_complete(self):
        return not self.running

    def jsonable(self):
        d = { 'message':self.message,
              'gameid':self.id,
              'level':self.level,
              'time':self.time }
        return d

    def finish(self, won, score):
        self.running = False
        self.won = won
        self.score = score
        # send update to server
        msg = { 'a':'update',
                'gameid': self.id,
                'running': False,
                'result': won,
                'score': score
                }
        self.client.socket.send(json.dumps(msg))

class FutureClient(object):
    """A FutureClient is a forward-thinking class ready to take on
    the risks and responsibilities that the future offers. Are you
    ready to extend FutureClient?"""
    
    def __init__(self,urlstring = "ws://localhost:8888/socket",name='Generic Client',max_games=1):
        self.name = name
        self.socket = create_connection(urlstring)
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
        msg = {
            'a':'status',
            'avail_slots':[x.jsonable() for x in self.message_slots if not x.in_use],
            'avail_games':[x.jsonable() for x in self.available_games if not x.running],
            'bored':len(self.running_games) == 0
            }
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
        self.stop()
        if self.thread:
            self.thread.join()
        # abort all games
        for game in self.available_games:
            game.cancel()
        self.socket.close()

