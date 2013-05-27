import serial
import serial.tools.list_ports as list_ports
import time
import struct

illum_count = 25




illum_count = 25

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
        # imap entries are (pressed, mode)
        self.imap = [(False,0)]*illum_count
        self.t.write('m\\x0cmBoot sequence\\ncomplete.\n')
        time.sleep(0.5)
        self.t.write('m\\x0c\n')
        for i in range(illum_count):
            self.t.write('i{0}:{1}\n'.format(i,0))
    def get_keypresses(self):
        ipressed = []
        self.tpp.write('r\n')
        keys = self.tpp.readline().strip()
        for i in range(illum_count):
            newp = keys[i]=='1'
            (oldp,mode) = self.imap[i]
            if (newp and not oldp):
                # button down press
                ipressed.append(i)
            self.imap[i] = (newp,mode)
        return ipressed
    def set_illuminated(self,i,mode):
        self.t.write('i{0}:{1}\n'.format(i,mode))
        (oldp, _) = self.imap[i]
        self.imap[i] = (oldp, mode)
    def set_led(self,i,mode):
        self.t.write('l{0}:{1}\n'.format(i,mode))
    def send_msg(self,msg):
        self.t.write('m{0}'.format(msg))

c = Controller()
while True:
    time.sleep(0.05)
    for i in c.get_keypresses():
        # button down press
        mode = (c.imap[i][1] + 1) % 5
        c.set_illuminated(i,mode)
