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


portNum = 8888

game = Game()

class GameThread(threading.Thread):
    def run(self):
        while True:
            pass
            
class SpaceteamSocket(websocket.WebSocketHandler):
    def open(self):
        self.active_games = []

    def on_message(self, message):
        command = json.loads(message)
        if command.get('a') == 'register':
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
    tornado.ioloop.IOLoop.instance().start()


