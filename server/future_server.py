import tornado.ioloop
import tornado.web
from tornado import websocket
import json
import time

# Refactoring: all requests start at the consoles. A supervisory thread
# takes care of console timeouts, etc.
class Game:
    """The game object manages the console list and any global
    information like score, game time, etc."""
    def __init__(self):
        self.consoles = {}
        self.next_id = 0
    def add_console(self,console):
        console.id = self.next_id
        self.next_id = self.next_id + 1
        self.consoles[console.id] = console
        print "+ Added {0} console, id {1}".format(console.name,console.id)
    def remove_console(self,console):
        if self.consoles.has_key(console.id):
            del self.consoles[console.id]
            print "- Removed {0} console, id {1}".format(console.name,console.id)
        else:
            print "*** Attempted to remove console {0}, id {1}".format(console.name,console.id)
    def get_console(self,id):
        return self.consolles.
        self.game_lock.acquire()
    def get_all_consoles(self):
        self.game_lock.acquire()
        consoles = self.consoles.copy()
        self.game_lock.release()
        return consoles

portNum = 8888

game = Game()

class GameThread(threading.Thread):
    def run(self):
        print "Starting game thread..."
        while True:
            #
            time.sleep(0.1)
            game.find_available_consoles()
            
class SpaceteamSocket(websocket.WebSocketHandler):
    def open(self):
        self.active_games = []
        self.pending_calls = {}
        self.next_qid = 100

    def write_query(self,msg,callback):
        qid = self.next_qid
        msg['qid']=qid
        self.next_qid = self.next_qid + 1
        self.pending_calls[qid]=callback
        self.write_message(msg)

    def on_message(self, message):
        command = json.loads(message)
        qid = command.get('qid')
        if qid:
            callback = self.pending_calls[qid]
            del self.pending_calls[qid]
            callback(self, message)
        elif command.get('a') == 'register':
            self.name = command.get('name')
            print 'registering',self.name
            game.add_console(self)
            rsp = { 'ok':True, 'id':self.id }
            self.write_message(json.dumps(rsp))
       
    def on_close(self):
        game.remove_console(self)


application = tornado.web.Application([
    (r"/socket", SpaceteamSocket),
])

if __name__ == "__main__":
    application.listen(portNum)
    print("FC server starting; listening on port {0}.".format(portNum))
    game_thread = GameThread()
    game_thread.daemon = True
    game_thread.start()
    tornado.ioloop.IOLoop.instance().start()


