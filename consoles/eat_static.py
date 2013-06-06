#!/usr/bin/python

from subprocess import call
import time

def make_static():
    call(['tvservice','--explicit="CEA 16"'])

def make_normal(x,y):
    call(['tvservice','--sdtv="NTSC 4:3"'])
    call(['fbset', '-xres', x, '-yres', y])

print "Let them eat static."
make_static()
time.sleep(0.5)
make_normal(320,200)
