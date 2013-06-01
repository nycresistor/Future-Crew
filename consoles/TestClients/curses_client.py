from future_client import FutureClient, Game, MessageSlot
import time
import threading
import curses

stdscr = curses.initscr()
stdscr.nodelay(True)
curses.noecho()
curses.cbreak()

class PressGame(Game):
    def __init__(self,name,message,button):
        self.button = button
        super(PressGame, self).__init__(name, message)
        self.condition = threading.Condition()

    def play_game(self):
        self.condition.acquire()
        self.condition.wait(2)
        self.condition.release()
        if not self.running:
            return
        self.update_message('PRESS BUTTON '+self.button+' NOW!!!')
        self.condition.acquire()
        self.condition.wait(2)
        self.condition.release()
        if self.running:
            self.finish(False,-5);

    def on_start(self):
        t = threading.Thread(target = self.play_game)
        self.thread = t
        t.start()

    def on_keypress(self,key):
        if self.running and key.lower() == self.button.lower():
            self.finish(True,5)
            self.condition.acquire()
            self.condition.notifyAll()
            self.condition.release()


games = [
    PressGame('pg1','Press button A.','A'),
    PressGame('pg2','Press button B.','B')
]

class PressMessageSlot(MessageSlot):
    def __init__(self, id=None, length=40, x=0, y=0):
        self.x = x
        self.y = y
        super(PressMessageSlot, self).__init__(id,length)

    def on_message(self,text):
        global stdscr
        stdscr.move(self.y,self.x)
        stdscr.clrtoeol()
        if (text):
            stdscr.addstr(self.y,self.x,text,curses.A_BLINK|curses.A_BOLD)

slots = [ PressMessageSlot(1,50,10,2) ]

if __name__ == '__main__':
    fc = FutureClient('ws://localhost:8888/socket','basic test client')
    fc.available_games = games
    fc.message_slots = slots
    fc.start()
    while True:
        c = stdscr.getch()
        if c > 0:
            c = chr(c)
            stdscr.addstr(5,0,"last keypress: "+c)
            if c == 'q' or c == 'Q':
                break
            else:
                for game in games:
                    game.on_keypress(c)
        time.sleep(0.05)
    fc.quit()

curses.nocbreak()
curses.echo()
curses.endwin()


