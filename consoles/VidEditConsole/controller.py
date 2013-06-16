from future_client import FutureClient, Game, MessageSlot
import serial
import serial.tools.list_ports as list_ports
import time
import struct
import random
import threading

illum_count = 25
led_count = 12

helices = {
    'D':1,'C':2,'B':3,'A':4,'G':5,'F':6,'E':7
}

boosters = {
    '1':24,
    '2':23,
    '3':22,
    '4':21,
    '5':20
}

buttongame_map = {
    'Dump Core':0,
    'PURGE NOW':8,
    'Elide Nesting':9,
    'Enable Life Support':10,
    'Semiaxis Out':12,
    'Escape Timeline':13,
    'Jump to Parallel Timeline':14,
    'Accelerate Timeline':15,
    'Advance Timeline':16,
    'Halt Timeline':17,
    'Reverse Timeline':18,
    'RELOAD CORE':19,
}

class ButtonGame(Game):
    def __init__(self,c):
        self.c = c
        super(ButtonGame, self).__init__('button_game')

    def make_indices_and_msg(self):
        elements = random.sample(buttongame_map.items(),1)
        msg = ' and '.join(map(lambda x:x[0],elements))
        indices = map(lambda x:x[1],elements)
        print indices, msg
        return (indices,msg)

    def play_game(self):
        (targets,msg) = self.make_indices_and_msg()
        self.update_message(msg)
        for idx in range(illum_count):
            if idx in targets:
                self.c.set_illuminated(idx,random.choice([0,0,0,0,2,3,4]))
            else:
                if random.randint(0,2) == 1:
                    self.c.set_illuminated(idx,random.choice([0,0,0,0,1,2,2,3,3]))
        starttime = time.time()
        duration = 8.5 + (2.0 * len(targets))
        while self.is_running() and (time.time()-starttime) < duration:
            if not self.wait(0.05):
                return
            for i in self.c.get_keypresses():
                if i in targets:
                    self.c.set_illuminated(i,1)
                    targets.remove(i)
            if not targets:
                self.finish(3)
                return
        self.finish(-5);

class HelicesGame(ButtonGame):
    def make_indices_and_msg(self):
        k = random.randint(1,8)
        if (k >= len(helices)):
            return (helices, 'ACTIVATE ALL HELICES')
        else:
            elements = random.sample(helices,k)
            msg = 'Activate Helix '+', '.join(elements)
            return (elements,msg)


class BoostersGame(ButtonGame):
    def make_indices_and_msg(self):
        k = random.randint(1,8)
        if (k >= len(boosters)):
            return (boosters, 'ENGAGE ALL BOOSTERS')
        else:
            elements = random.sample(boosters,k)
            msg = 'Engage Booster '+', '.join(elements)
            return (elements,msg)


class Controller:
    def __init__(self):
        ports={}
        for (name,_,_) in list_ports.grep('/dev/ttyACM*'):
            port = serial.Serial(name, timeout=3)
            port.write('I\n')
            teensyid = port.readline().strip()
            ports[teensyid] = port
        for (i,p) in ports.items():
            print("Found {0}".format(i))
        self.t=ports['teensy']
        self.tpp=ports['teensypp']
        self.t3=ports['teensy3']
        self.tlock = threading.RLock()
        self.tpplock = threading.RLock()
        self.t3lock = threading.RLock()
        # imap entries are (pressed, mode)
        self.imap = [(False,0)]*illum_count
        self.tlock.acquire()
        self.t.write('m\\x0cmBoot sequence\\ncomplete.\n')
        time.sleep(0.5)
        self.t.write('m\\x0c\n')
        for i in range(illum_count):
            self.set_illuminated(i,0)
        self.tlock.release()

    def get_knobs(self):
        self.t3lock.acquire()
        self.t3.write('r\n')
        knobs = self.t3.readline().strip()
        self.t3lock.release()
        return map(lambda x:map(int,x.split('/')),knobs.split())

    def get_keypresses(self):
        ipressed = []
        self.tpplock.acquire()
        self.tpp.write('r\n')
        keys = self.tpp.readline().strip()
        self.tpplock.release()
        for i in range(illum_count):
            newp = keys[i]=='1'
            (oldp,mode) = self.imap[i]
            if (newp and not oldp):
                # button down press
                ipressed.append(i)
            self.imap[i] = (newp,mode)
        return ipressed
    def set_illuminated(self,i,mode):
        self.tlock.acquire()
        self.t.write('i{0}:{1}\n'.format(i,mode))
        self.tlock.release()
        (oldp, _) = self.imap[i]
        self.imap[i] = (oldp, mode)
    def set_led(self,i,mode):
        self.tlock.acquire()
        self.t.write('l{0}:{1}\n'.format(i,mode))
        self.tlock.release()
    def set_light(self,colors):
        self.tlock.acquire()
        all_colors = list('rgb')
        colors = list(colors)
        for color in all_colors:
            m='p'+color
            if color in colors: m += '+\n'
            else: m += '-\n'
            self.t.write(m)
        self.tlock.release()
    def send_msg(self,msg,clear=True):
        if msg == None:
            msg = ''
        if clear:
            msg = '\x0c'+msg
        msg = msg.replace('\n','\\n')
        self.tlock.acquire()
        self.t.write('m{0}\n'.format(msg))
        self.tlock.release()



class PressBlinkersGame(Game):
    def __init__(self,c):
        super(PressBlinkersGame, self).__init__('blinkers','Disable blinking buttons')
        self.c = c
        self.candidates = set(range(illum_count))
        self.candidates.remove(11) # #11 doesn't illuminate :(

    def make_blinkers(self):
        count = random.randint(4,10)
        self.blinkers=set(random.sample(self.candidates,count))

    def play_game(self):
        self.make_blinkers()
        for i in range(illum_count):
            if i in self.blinkers:
                c.set_illuminated(i,4)
            else:
                c.set_illuminated(i,0)
        starttime = time.time()
        while self.is_running() and (time.time()-starttime) < 10.0:
            if not self.wait(0.05):
                return
            for i in c.get_keypresses():
                if i in self.blinkers:
                    c.set_illuminated(i,0)
                    self.blinkers.remove(i)
            if len(self.blinkers) == 0:
                self.finish(5)
                return
        self.finish(-5);

class SyncBlinkersGame(Game):
    def __init__(self,c):
        super(SyncBlinkersGame, self).__init__('synchronize','Synchronize blinking buttons')
        self.c = c
        self.candidates = set(range(illum_count))
        self.candidates.remove(11) # #11 doesn't illuminate :(

    def make_blinkers(self):
        count = random.randint(6,14)
        part = count/2
        self.a=set(random.sample(self.candidates,count))
        self.b=set(random.sample(self.a,part))
        self.a=self.a.difference(self.b)

    def play_game(self):
        self.make_blinkers()
        for i in range(illum_count):
            if i in self.a:
                c.set_illuminated(i,2)
            elif i in self.b:
                c.set_illuminated(i,3)
            else:
                c.set_illuminated(i,0)
        starttime = time.time()
        while self.is_running() and (time.time()-starttime) < 15.0:
            if not self.wait(0.05):
                return
            for i in c.get_keypresses():
                if i in self.a:
                    c.set_illuminated(i,3)
                    self.a.remove(i)
                    self.b.add(i)
                elif i in self.b:
                    c.set_illuminated(i,2)
                    self.b.remove(i)
                    self.a.add(i)
            if (len(self.a) == 0) or (len(self.b) == 0):
                self.finish(5)
                return
        self.finish(-5);

class LCDSlot(MessageSlot):
    def __init__(self, c, id=None, length=40):
        self.c = c
        super(LCDSlot, self).__init__(id,length)

    def on_message(self,text):
        self.c.send_msg(text)

c = Controller()

c.set_light('r')

games = [
    ButtonGame(c),
    HelicesGame(c),
    BoostersGame(c),
#    PressBlinkersGame(c),
#    SyncBlinkersGame(c)
]

slots = [
]

class VidEditClient(FutureClient):
    def __init__(self,controller):
        self.c = controller
        super(VidEditClient,self).__init__(name='VidEditConsole')

    def on_session_start(self,message):
        c.set_light('b')

    def on_session_fail(self,message,score):
        c.set_light('r')

    def on_session_success(self,message,score):
        c.set_light('g')

import sys

if __name__ == '__main__' and len(sys.argv) == 1:
    fc = VidEditClient(c)
    fc.available_games = games
    fc.message_slots = slots
    fc.start()
    try:
        while True:
            time.sleep(0.05)
    except:
        fc.quit()
else:
    # test mode
    for i in range(led_count):
        c.set_led(i,1)
        time.sleep(0.1)
        c.set_led(i,0)
    for i in range(illum_count):
        c.set_illuminated(i,1)
        time.sleep(0.1)
        c.set_illuminated(i,0)
    while True:
        for i in c.get_keypresses():
            print i," ",
        for (a,b) in c.get_knobs():
            print "{0}-{1} ".format(a,b),
        print ""

