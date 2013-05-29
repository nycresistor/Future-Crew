from websocket import create_connection
import json
import time

class RegistrationError(Exception):
    pass

class MessageSlot:
    def __init__(self,id,l):
        self.id = id
        self.length = l
    def on_message(self,text):
        print "MESSAGE: ",text
    def jsonable(self):
        return {
            'id':self.id,
            'len':self.length
            }

class ClientGame:
    def __init__(self, gameid, message, level =-1, time =-1):
        self.id = gameid
        self.running = False
        self.message = message
        self.time = time
        self.level = level
    def on_start(self):
        self.start_time = time.time()
        self.running = True
        print "Game {0} started!".format(self.id)
        pass
    def on_cancel(self):
        self.running = False
        print "Game {0} cancelled!".format(self.id)
        pass
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

class FutureClient:
    """A FutureClient is a forward-thinking class ready to take on
    the risks and responsibilities that the future offers. Are you
    ready to extend FutureClient?"""
    
    def __init__(self,urlstring = "ws://localhost:8888/socket",name='Generic Client'):
        self.name = name
        self.socket = create_connection(urlstring)
        self.running_games = []
        msg = {'a':'register','name':self.name}
        self.socket.send(json.dumps(msg))
        self.message_slots = []
        self.available_games = []
    def on_game_start(self,game):
        print("Game {0} started".format(game.id))
        pass
    def on_game_end(self,game,won,score):
        print("Game {0} ended, {1}, {2}".format(game.id,won,score))
        pass
    def status(self):
        msg = {
            'a':'status',
            'avail_slots':[x.jsonable() for x in self.message_slots],
            'avail_games':[x.jsonable() for x in self.available_games],
            'bored':len(self.running_games) == 0
            }
        self.socket.send(json.dumps(msg))

    def quit(self):
        self.socket.close()

