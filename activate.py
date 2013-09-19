#!/usr/bin/python
import subprocess

from os.path import expanduser
homepath = expanduser("~")

def remote(ip, start, services):
    if start:
        c = "start"
    else:
        c = "stop"
    cmdstr = '; '.join(["sudo /etc/init.d/{} {}".format(x,c) for x in services])
    l = ['ssh','-i',homepath+'/pi-key','pi@{}'.format(ip),cmdstr]
    process = subprocess.Popen(l)
    process.communicate()

nodes={'videdit':('192.168.1.98',["invasion","VidEditConsole"]),
       'patch':('192.168.1.97',["invasion","PatchConsole"]),
       'piano':('192.168.1.96',["ToyPianoConsole"]),
       'teletype':('192.168.1.95',["TeletypeConsole"]),
       'rotary':('192.168.1.94',["RotaryConsole"]),
       'server':('192.168.1.99',["FCServer"])
}

import sys

if __name__=='__main__':
    enable = True
    for arg in sys.argv:
        if arg == '-e': enable=True
        elif arg == '-d': enable=False
        elif arg == '--off':
            for (ip,services) in nodes.values():
                remote(ip,False,services)
        elif arg == '--on':
            for (ip,services) in nodes.values():
                remote(ip,True,services)
        else:
            if arg in nodes:
                (ip,services) = nodes[arg]
                remote(ip,enable,services)
