from websocket import create_connection
import json

if __name__ == '__main__':
    ws = create_connection("ws://localhost:8888/socket")
    
    msg = {'a': 'register', 'name': 'client2.py'}
    ws.send(json.dumps(msg))
    rsp = ws.recv()
    print rsp

    msg = {'a': 'relay', 'd': 125, 'm': 'I <3 marshmallows.'}
    ws.send(json.dumps(msg))

    ws.close()

