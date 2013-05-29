from future_client import FutureClient, Game, MessageSlot
import time

if __name__ == '__main__':
    fc = FutureClient('ws://localhost:8888/socket','client2.py w/ lib')
    fc.available_games = [
        Game('test1','MUST PRESS BUTTON'),
        Game('test2','MUST PRESS BUTTON NOW',time=3.2)
        ]
    fc.message_slots = [
        MessageSlot(1,50)
        ]

    fc.start()
    print "Manual stop."
    #fc.quit()



