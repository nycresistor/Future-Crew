from future_client import FutureClient, ClientGame, MessageSlot
import time

if __name__ == '__main__':
    fc = FutureClient('ws://localhost:8888/socket','client2.py w/ lib')
    fc.available_games = [
        ClientGame('test1','MUST PRESS BUTTON'),
        ClientGame('test2','MUST PRESS BUTTON NOW',time=3.2)
        ]
    fc.message_slots = [
        MessageSlot(1,50)
        ]
    print "Start pings..."
    for i in range(100):
        fc.status()
        time.sleep(0.2)

    print "Stop pings..."

    # two seconds in server should hang up on you
    time.sleep(5)

    print "Manual stop."
    fc.quit()



