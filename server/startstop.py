from websocket import create_connection, socket
import json
import time
import threading
from sys import argv
from os import getenv

urlstring = None

if __name__=='__main__':
    if not urlstring:
        urlstring = getenv('SERVER_URL',"ws://localhost:2600/socket")
    try:
        socket = create_connection(urlstring,5.0)
    except socket.error:
        print "Could not connect to server. Trying again."
        time.sleep(1.5)

    msg = {}
    if argv[1] == 'start':
        msg = {'a':'session_start'}
        socket.send(json.dumps(msg))
    elif argv[1] == 'abort':
        msg = {'a':'session_abort'}
        socket.send(json.dumps(msg))
        
