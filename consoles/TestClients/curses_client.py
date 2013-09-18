from future_client import FutureClient, Game, MessageSlot
import time
import threading
import curses

stdscr = curses.initscr()
stdscr.nodelay(True)
curses.noecho()
curses.cbreak()

class PressGame(Game):
    def __init__(self,name,prefix,message,button):
        self.button = button
        self.prefix = prefix
        super(PressGame, self).__init__(name, prefix+": "+message)

    def play_game(self):
        if not self.wait(5):
            return
        self.update_message(self.prefix+': PRESS BUTTON '+self.button+' NOW!!!')
        if not self.wait(5):
            return
        self.finish(-5,self.prefix+":Too slow!")

    def on_keypress(self,key):
        if self.is_running() and key.lower() == self.button.lower():
            self.finish(5,self.prefix+":Success")




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

class FC_curses(FutureClient):
    def on_drop(self):
        stdscr.addstr(0,0,"CONNECTION DROP",curses.A_BOLD)


import sys
if __name__ == '__main__':
    try:
        if len(sys.argv)>1:
            name=sys.argv[1]
        else:
            name='test'
        fc = FC_curses(name=name)
        games = [
            PressGame('pg1',name,'Press button A.','A'),
            PressGame('pg2',name,'Press button B.','B') ]
        fc.available_games = games
        fc.message_slots = slots
        fc.start()

        stdscr.addstr(0,0,"Console "+name+" Client running; type 'q' to quit",curses.A_BOLD)
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
    finally:
        curses.nocbreak()
        curses.echo()
        curses.endwin()



