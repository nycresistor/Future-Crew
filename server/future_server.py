from tornado.ioloop import IOLoop, PeriodicCallback
import tornado.web
from tornado import websocket
import json
import time

class Consoles:
    """The game object manages the console list and any global
    information like score, game time, etc."""
    def __init__(self):
        self.consoles = {}
        self.next_id = 0
    def add(self,console):
        console.id = self.next_id
        self.next_id = self.next_id + 1
        self.consoles[console.id] = console
        print "+ Added {0} console, id {1}".format(console.name,console.id)
    def remove(self,console):
        if self.consoles.has_key(console.id):
            del self.consoles[console.id]
            print "- Removed {0} console, id {1}".format(console.name,console.id)
        else:
            print "* No such console {0}, id {1}".format(console.name,console.id)
    def get(self,id):
        return self.consoles[id]

portNum = 8888
            
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
        if command.get('a') == 'register':
            self.name = command.get('name')
            print 'registering',self.name
            #game.add_console(self)
            rsp = { 'ok':True, 'id':self.id }
            self.write_message(json.dumps(rsp))
       
    def on_close(self):
        #game.remove_console(self)
        pass


application = tornado.web.Application([
    (r"/socket", SpaceteamSocket),
])

def heartbeat():
    print "ping"

if __name__ == "__main__":
    application.listen(portNum)
    print("FC server starting; listening on port {0}.".format(portNum))
    pc = PeriodicCallback(heartbeat,1000,IOLoop.instance())
    pc.start()
    IOLoop.instance().start()


