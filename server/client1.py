from websocket import create_connection
import json

if __name__ == '__main__':
    ws = create_connection("ws://localhost:8888/socket")
    
    msg = {'a': 'register_me', 'id': 123}
    ws.send(json.dumps(msg))
    
    while(True):
        result =  ws.recv()
        print "Received '%s'" % result

    ws.close()
