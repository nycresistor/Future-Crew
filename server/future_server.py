import tornado.ioloop
import tornado.web
from tornado import websocket
import json

GLOBALS = {
    'sockets': [],
    'consoles': {},
}

class SpaceteamSocket(websocket.WebSocketHandler):
    def open(self):
        GLOBALS['sockets'].append(self)
        print GLOBALS['sockets']
        print "SPACE socket opened"

    def on_message(self, message):
        command = json.loads(message)
        if command.get('a') == 'register_me':
            GLOBALS['consoles'][command.get('id')] = self
        elif command.get('a') == 'relay':
            GLOBALS['consoles'][command.get('d')].write_message(command.get('m'))
       
    def on_close(self):
        print "SPACE socket closed"
        print GLOBALS['consoles']
        GLOBALS['sockets'].remove(self)


application = tornado.web.Application([
    (r"/socket", SpaceteamSocket),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
