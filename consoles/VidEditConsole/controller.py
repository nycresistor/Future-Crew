import serial
import serial.tools.list_ports as list_ports
import time
import struct

ports={}

for (name,_,_) in list_ports.grep('/dev/ttyACM*'):
    port = serial.Serial(name, timeout=3)
    port.write('I\n')
    teensyid = port.readline().strip()
    ports[teensyid] = port

for (i,p) in ports.items():
    print("Found {0}".format(i))

t=ports['teensy']
tpp=ports['teensypp']

illum_count = 25

# imap entries are (pressed, mode)
imap = [(False,0)]*illum_count

for i in range(illum_count):
    t.write('i{0}:{1}\n'.format(i,0))
    
while True:
    time.sleep(0.05)
    tpp.write('r\n')
    keys = tpp.readline().strip()
    for i in range(illum_count):
        newp = keys[i]=='1'
        (oldp,mode) = imap[i]
        if (newp and not oldp):
            # button down press
            mode = (mode + 1) % 5
            t.write('i{0}:{1}\n'.format(i,mode))
            print('Button {0} pressed'.format(i))
        imap[i] = (newp,mode)
