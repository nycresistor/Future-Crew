#!/bin/bash
cd /home/pi/Future-Crew/consoles/VidEditConsole
script -e -c 'python invasion.py' /dev/null
exit $?


