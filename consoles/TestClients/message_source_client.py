from future_client import FutureClient, Game, MessageSlot
import time
import threading

count = 0
def next_id():
    global count
    count += 1
    return str(count)

class NothingGame(Game):
    def __init__(self,name,message):
        super(NothingGame, self).__init__(name, message)

    def play_game(self):
        self.update_message(self.id+': message '+next_id())
        if not self.wait(2):
            return
        self.update_message(self.id+': further message '+next_id())
        if not self.wait(2):
            return
        self.finish(1)

games = [
    NothingGame('A','Initial Message A'),
    NothingGame('B','Initial Message B'),
]

if __name__ == '__main__':
    fc = FutureClient(name='basic transmission client',max_games=3)
    fc.available_games = games
    fc.message_slots = []
    fc.start()
    try:
        while True:
            time.sleep(0.05)
    finally:
        fc.quit()



