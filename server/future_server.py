from tornado.ioloop import IOLoop, PeriodicCallback
import tornado.web
from tornado import websocket
import json
import time

portNum = 8888

class Console:
    consoles = set()
    def __init__(self,name,socket):
        self.name = name
        self.socket = socket
        self.timestamp = time.clock()
        Console.consoles.add(self)
        print "+ Added {0} console".format(self.name)
    def remove(self):
        Console.consoles.remove(self)
        print "- Removed {0} console".format(self.name)
    def handle_msg(self,msg):
        self.timestamp = time.time()



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


