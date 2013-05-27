import tornado.ioloop
import tornado.web
from tornado import websocket
import json
import threading
import time

class Game:
    def __init__(self):
        self.consoles = {}
        self.game_lock = threading.Lock()
        self.next_id = 0
    def add_console(self,console):
        self.game_lock.acquire()
        console.id = self.next_id
        self.next_id = self.next_id + 1
        self.consoles[console.name] = console
        self.game_lock.release()
        print "+ Added {0} console, id {1}".format(console.name,console.id)
    def remove_console(self,console):
        self.game_lock.acquire()
        del self.consoles[console.name]
        self.game_lock.release()
        print "- Removed {0} console, id {1}".format(console.name,console.id)
    def status_callback(self,console,message):
        print "status from {0}: {1}".format(console,message)
    def find_available_consoles(self):
        self.game_lock.acquire()
        consoles = self.consoles.copy()
        self.game_lock.release()
        for_messages, for_games = [],[]
        status_msg = {'a':'status'}
        for (name,console) in self.consoles.items():
            console.write_query(status_msg,self.status_callback)


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


