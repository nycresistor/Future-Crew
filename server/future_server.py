from tornado.ioloop import IOLoop, PeriodicCallback
import tornado.web
from tornado import websocket
import json
import time
import random

portNum = 8888

class Game:
    '''A 'game' is a message displayed on one console, and a set
    of actions performed on a (usually different) console to 'win' the
    game. Games can time out or be cancelled.'''
    # maintain map of running games
    games = {}

    def __init__(self,message_console,slot_id,play_console,msg):
        self.message_console = message_console
        self.play_console = play_console
        self.msg = msg
        self.slot_id = slot_id
        self.id = (play_console,msg['gameid'])
        Game.games[self.id] = self

    def start(self):
        self.message_console.send_message(self.msg['message'],self.slot_id)
        self.play_console.send_control(self.msg,'start')

    def resolve(self,won,score):
        if won:
            print "BIG WINNER +{0} POINTS".format(score)
        else:
            print "small loser {0} points".format(score)
        message_console.send_message(None,self.slot_id)
        del games[self.gameid]
    
    def handle_game_update(self,update):
        if update['running']:
            # all is well, just status
            return
        else:
            won = update['result']
            score = update.get('score',0)
            self.resolve(won,score)
            del Game.games[(self.play_console,update['gameid'])]

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
        self.queued_message = None
        self.bored = False

    def send_message(self,message,slot):
        m_msg = {
            'a' : 'message',
            'text' : message,
            'slotid' : slot
            }
        self.socket.write_message(json.dumps(m_msg))

    def send_control(self,game,operation):
        p_msg = {
            'a' : 'control',
            'game' : game,
            'operation' : operation
            }
        self.socket.write_message(json.dumps(p_msg))

    def remove(self):
        Console.consoles.remove(self)
        print "- Removed {0} console".format(self.name)

    def wants_game(self):
        return self.bored and len(self.avail_games) > 0

    def has_slot(self):
        return self.queued_message == None and len(self.avail_slots) > 0

    def handle_status(self,msg):
        self.timestamp = time.time()
        self.avail_slots = msg.get('avail_slots',[])
        self.avail_games = msg.get('avail_games',[])
        self.bored = msg.get('bored',False)

class SpaceteamSocket(websocket.WebSocketHandler):
    def open(self):
        self.console = None
        self.cmdmap = {
            'register': self.on_register,
            'status': self.on_status,
            'update': self.on_update
            }

    def on_register(self, message):
        name = message['name']
        self.console = Console(name, self)

    def on_message(self, message):
        command = json.loads(message)
        self.cmdmap[command['a']](command)

    def on_status(self, message):
        self.console.handle_status(message)

    def on_update(self, msg):
        Game.games[(self.console,msg['gameid'])].handle_game_update(update)
            
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

def makeNewGame():
    bored = [x for x in Console.consoles if x.wants_game()]
    if bored:
        player = random.choice(bored)
        slotavail = [x for x in Console.consoles if x.has_slot()]
        if not slotavail:
            print("... Not enough message slots for bored client")
        else:
            game = random.choice(player.avail_games)
            messenger = random.choice(slotavail)
            slotid = random.choice(messenger.avail_slots)['id']
            g = Game(messenger,slotid,player,game)
            g.start()


def heartbeat():
    # check for client timeouts
    timestamp = time.time()
    for console in Console.consoles.copy():
        if (timestamp - console.timestamp) > TIMEOUT:
            print("* Console {0} timed out; closing socket".format(console.name))
            console.socket.close()
            console.remove()
    makeNewGame()

if __name__ == "__main__":
    application.listen(portNum)
    print("FC server starting; listening on port {0}.".format(portNum))
    pc = PeriodicCallback(heartbeat,100,IOLoop.instance())
    pc.start()
    IOLoop.instance().start()


