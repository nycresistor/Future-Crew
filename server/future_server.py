from tornado.ioloop import IOLoop, PeriodicCallback
import tornado.web
from tornado import websocket
import json
import time
import random
import ScoreTower
from os import getenv

portNum = getenv('SERVER_PORT',2600)

class Session:
    '''A 'session' is a set of games played in sequence-- basically,
    what the players think of as a complete 'game'. There is a single
    score for the entire session.'''

    def __init__(self):
        self.reset_values()

    def reset_values(self):
        self.score = 0
        self.state = None
        self.pos_score = 0
        self.neg_score = 0
        self.pos_threshold = 50;
        self.neg_threshold = -50;

    def start(self):
        self.reset_values()
        self.state = 'running'
	scoretower_begin()
        for console in Console.consoles.copy():
            console.send_session('starting','Future Crew is Go!', self.score)

    def abort(self):
        self.session_done(False)

    def session_done(self,won):
        print "Game is won:",won
        self.state = None
        if won:
            cmd = 'won'
            msg = 'Game is won!!!'
	    scoretower_won() # blink won sequence, return to attract
        else:
            cmd = 'lost'
            msg = 'Game is lost!!!'
	    scoretower_lost() # blink lost sequence, return to attract
        for console in Console.consoles.copy():
            console.send_session(cmd, msg, self.score)

    def game_done(self,won,score):
        self.score += score
        if score > 0: self.pos_score += score
        else: self.neg_score += score
        if self.pos_score > self.pos_threshold:
            self.session_done(True)
        elif self.neg_score < self.neg_threshold:
            self.session_done(False)

    def heartbeat(self):
        if self.state == 'running':
            for c in list(Console.consoles):
                if c.wants_game():
                    c.make_new_game()

session = Session()

class Game:
    '''A 'game' is a message displayed on one console, and a set
    of actions performed on a (usually different) console to 'win' the
    game. Games can time out or be cancelled.'''
    # maintain map of running games
    games = {}

    def __init__(self,message_console,slot_id,play_console,msg):
        self.message_console = message_console
        self.play_console = play_console # the console playing the game
        self.msg = msg
        self.slot_id = slot_id
        self.id = (play_console,msg['gameid'])
        Game.games[self.id] = self

    def start(self):
        print(": starting game, {0}:{1} --> {2}:{3}".format(
                self.play_console.name,
                self.id[1],
                self.message_console.name,
                self.slot_id))
        self.message_console.send_message(self.msg['message'],self.slot_id)
        self.play_console.send_control(self.msg,'start')

    def resolve(self,won,score):
	# self.play_console.name returns the name of the console.
        session.game_done(won,score)
        if won:
	    scoretower_hit(self.play_console.name, score) 
            print "+ Game {0} won, {1} points".format(self.id[1],score)
        else:
	    scoretower_miss(self.play_console.name, score) 
            print "- Game {0} lost, {1} points".format(self.id[1],score)
        self.message_console.send_message(None,self.slot_id)
    
    def handle_game_update(self,update):
        if update['running']:
            # all is well, just status
            if update.has_key('message'):
                self.message_console.send_message(update['message'],self.slot_id)
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
        self.timestamp = time.time()
        Console.consoles.add(self)
        print "+ Added {0} console".format(self.name)
        self.avail_slots = []
        self.avail_games = []
        self.queued_message = None
        self.bored = False
        self.last_game_start = time.time()

    def send_message(self,message,slot):
        m_msg = {
            'a' : 'message',
            'text' : message,
            'slotid' : slot
            }
        try:
            self.socket.write_message(json.dumps(m_msg))
        except:
            print "Can't send message; possible that client has dropped!"

    def send_session(self,state,message,score):
        s_msg = {
            'a':'session_update',
            'state':state,
            'message':message,
            'score':score
            }
        try:
            self.socket.write_message(json.dumps(s_msg))
        except:
            print "Can't send message; possible that client has dropped!"

    def send_control(self,game,operation):
        p_msg = {
            'a' : 'control',
            'game' : game,
            'operation' : operation
            }
        try:
            self.socket.write_message(json.dumps(p_msg))
        except:
            print "Can't send control; possible that client has dropped!"

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

    def make_new_game(self):
        # minimum interval between games: 2 seconds
        if (time.time() - self.last_game_start) < 2.0:
            return False
        slotavail = [x for x in Console.consoles if x.has_slot()]
        if not slotavail:
            # print("... Not enough message slots for bored client")
            pass
        else:
            self.last_game_start = time.time()
            game = random.choice(self.avail_games)
            messenger = random.choice(slotavail)
            slotid = random.choice(messenger.avail_slots)['id']
            g = Game(messenger,slotid,self,game)
            g.start()
            return True
        return False

class SpaceteamSocket(websocket.WebSocketHandler):
    def open(self):
        self.console = None
        self.cmdmap = {
            'register': self.on_register,
            'status': self.on_status,
            'update': self.on_update,
            'session_start': self.on_start,
            'session_abort': self.on_abort
            }

    def on_register(self, message):
        name = message['name']
        self.console = Console(name, self)

    def on_message(self, message):
        command = json.loads(message)
        self.cmdmap[command['a']](command)

    def on_status(self, message):
        self.console.handle_status(message)

    def on_abort(self, message):
        session.abort()

    def on_start(self, message):
        session.start()

    def on_update(self, msg):
        try:
            Game.games[(self.console,msg['gameid'])].handle_game_update(msg)
        except KeyError:
            print "Update message sent for obsolete game {0}".format(msg['gameid'])
            
    def on_close(self):
        if self.console:
            self.console.socket = None
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
    session.heartbeat()

if __name__ == "__main__":
    application.listen(portNum, '0.0.0.0')
    print("FC server starting; listening on port {0}.".format(portNum))
    pc = PeriodicCallback(heartbeat,100,IOLoop.instance())
    pc.start()
    IOLoop.instance().start()


