from websocket import create_connection
import json
import time

if __name__ == '__main__':
    ws = create_connection("ws://localhost:8888/socket")
    
    msg = {'register' : 'client2.py'}
    ws.send(json.dumps(msg))
    rsp = ws.recv()
    print rsp

    print "Start pings..."
    msg = {
        'avail_slots':[],
        'game_updates':[],
        'avail_games':[]
        }
    for i in range(10):
        ws.send(json.dumps(msg))
        time.sleep(0.2)

    print "Stop pings..."

    # two seconds in server should hang up on you
    time.sleep(4)

    print "Manual stop."
    ws.close()



