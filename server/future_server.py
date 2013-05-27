from tornado.ioloop import IOLoop, PeriodicCallback
import tornado.web
from tornado import websocket
import json
import time

portNum = 8888

class Game:
    '''A 'game' is a message displayed on one console, and a set
    of actions performed on a (usually different) console to 'win' the
    game. Games can time out or be cancelled.'''
    games = {}

    def __init__(self,gameid,message_console,play_console,descr):
        self.message_console = message_console
        self.play_console = play_console
        self.descr = descr
        Game.games[gameid] = self

    def dispatch_update(update):
        Game.games[update.gameid].handle_game_update(update)

    def resolve(self,won,score):
        if won:
            print "BIG WINNER +{0} POINTS".format(score)
        else:
            print "small loser {0} points".format(score)
        message_console.resolve_message(self,won,score)
        play_console.resolve_game(self,won,score)
        del games[self.gameid]
    
    def handle_game_update(self,update):
        if update.running:
            # all is well, just status
            return
        else:
            won = update['result']
            score = update.get('score',0)
            self.resolve(won,score)

class Console:
    consoles = set()
    def __init__(self,name,socket):
        self.name = name
        self.socket = socket
        self.timestamp = time.clock()
        Console.consoles.add(self)
        print "+ Added {0} console".format(self.name)
        self.avail_slots = []
        self.avail_games = []
        self.playing = set()
        self.showing = set()
    def resolve_message(self,game,won,score):
        self.showing.remove(game)
    def resolve_game(self,game,won,score):
        self.playing.remove(game)
    def remove(self):
        Console.consoles.remove(self)
        print "- Removed {0} console".format(self.name)
    def handle_msg(self,msg):
        self.timestamp = time.time()
        self.avail_slots = msg.get('avail_slots',[])
        self.avail_games = msg.get('avail_games',[])
        for update in msg.get('game_updates',[]):
            Game.dispatch_update(update)

class SpaceteamSocket(websocket.WebSocketHandler):
    def open(self):
        self.console = None

    def on_message(self, message):
        command = json.loads(message)
        if command.has_key('register'):
            name = command['register']
            self.console = Console(name, self)
            rsp = { 'ok':True }
            self.write_message(json.dumps(rsp))
        else:
            self.console.handle_msg(command)
            rsp = { 'ok':True,
                    'game_control':[],
                    'messages':[],
                    'master_state':{}
                    }
            self.write_message(json.dumps(rsp))
            
    def on_close(self):
        if self.console:
            try:
                self.console.remove()
            except KeyError:
                # may already have been removed by timeout
                pass

application = tornado.web.Application([
    (r"/socket", SpaceteamSocket),
])

TIMEOUT = 2.0

def heartbeat():
    # check for client timeouts
    timestamp = time.time()
    for console in Console.consoles.copy():
        if (timestamp - console.timestamp) > TIMEOUT:
            print("* Console {0} timed out; closing socket".format(console.name))
            console.socket.close()
            console.remove()


if __name__ == "__main__":
    application.listen(portNum)
    print("FC server starting; listening on port {0}.".format(portNum))
    pc = PeriodicCallback(heartbeat,100,IOLoop.instance())
    pc.start()
    IOLoop.instance().start()


