#!/usr/bin/python

from subprocess import call
import time


def make_static():
    call(['tvservice','--explicit=CEA 16'])

def set_res(x,y):
    call(['fbset', '-xres', str(x), '-yres', str(y)])

def make_normal(x,y):
    call(['tvservice','--sdtv=NTSC 4:3'])
    set_res(x,y+1)
    set_res(x,y)

print "Let them eat static."
make_static()
time.sleep(0.5)
make_normal(320,200)
