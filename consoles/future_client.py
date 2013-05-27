from websocket import create_connection
import json
import time

class RegistrationError(Exception):
    pass

class FutureClient:
    """A FutureClient is a forward-thinking class ready to take on
    the risks and responsibilities that the future offers. Are you
    ready to extend FutureClient?"""
    
    def __init__(self,urlstring = "ws://localhost:8888/socket",name='Generic Client'):
        self.name = name
        self.socket = create_connection(urlstring)
        msg = {'register':self.name}
        self.socket.send(json.dumps(msg))
        rsp = json.loads(self.socket.recv())
        if rsp.get('ok',False) != True:
            raise RegistrationError("Bad registration response "+json.dumps(rsp))
        self.message_slots = []
        self.available_games = []
    def on_game_start(self,gameid):
        print("Game {0} started".format(gameid))
        pass
    def on_game_end(self,gameid,won,score):
        print("Game {0} ended, {1}, {2}".format(gameid,won,score))
        pass
    def update(self):
        msg = {
            'avail_slots':self.message_slots,
            'avail_games':self.available_games,
            'game_updates':[]
            }
        self.socket.send(json.dumps(msg))
        rsp = json.loads(self.socket.recv())
    def quit(self):
        self.socket.close()

