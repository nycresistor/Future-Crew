from websocket import create_connection
import json

if __name__ == '__main__':
    ws = create_connection("ws://localhost:8888/socket")
    
    msg = {'a': 'register_me', 'id': 125}
    ws.send(json.dumps(msg))

    msg = {'a': 'relay', 'd': 123, 'm': 'I <3 marshmallows.'}
    ws.send(json.dumps(msg))

    ws.close()

