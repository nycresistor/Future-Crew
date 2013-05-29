from future_client import FutureClient, Game, MessageSlot
import time

class PressGame(Game):
    def __init__(self,name,message,button):
        super(PressGame, self).__init__(name, message)

pg1 = PressGame('pg1','PRESS BUTTON A','A')
pg2 = PressGame('pg2','PRESS BUTTON B','B')

if __name__ == '__main__':
    fc = FutureClient('ws://localhost:8888/socket','client2.py w/ lib')
    fc.available_games = [
        pg1, pg2
        ]
    fc.message_slots = [
        MessageSlot(1,50)
        ]

    fc.start()
    print "Manual stop."
    #fc.quit()



