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
    def add_console(self,console):
        self.game_lock.acquire()
        self.consoles[console.name] = console
        self.game_lock.release()
    def remove_console(self,console):
        self.game_lock.acquire()
        del self.consoles[console.name]
        self.game_lock.release()


portNum = 8888

game = Game()

class GameThread(threading.Thread):
    def run(self):
        while True:
            pass
            
class SpaceteamSocket(websocket.WebSocketHandler):
    id_lock = threading.Lock()
    next_id = 0

    def open(self):
        SpaceteamSocket.id_lock.acquire()
        self.id = SpaceteamSocket.next_id
        SpaceteamSocket.next_id = SpaceteamSocket.next_id + 1
        SpaceteamSocket.id_lock.release()
        print "- New connection, assigned id {0}".format(self.id)
        self.active_games = []

    def on_message(self, message):
        command = json.loads(message)
        if command.get('a') == 'register':
            self.name = command.get('name')
            print 'registering',self.name
            GLOBALS['consoles'][self.id] = self
            rsp = { 'ok':True, 'id':self.id }
            self.write_message(json.dumps(rsp))
       
    def on_close(self):
        print "SPACE socket closed"
        print GLOBALS['consoles']
        GLOBALS['sockets'].remove(self)


application = tornado.web.Application([
    (r"/socket", SpaceteamSocket),
])

if __name__ == "__main__":
    application.listen(portNum)
    print("FC server starting; listening on port {0}.".format(portNum))    
    tornado.ioloop.IOLoop.instance().start()


