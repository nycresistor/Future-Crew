#!/bin/sh

APP_NAME="RotaryConsole"
APP_PATH="/home/pi/Future-Crew/consoles/RotaryConsole"
APP_USER=pi

case "$1" in
  start)
    echo -n "Starting $APP_NAME..."
    PYTHONPATH=.. start-stop-daemon --start \
                      --background \
                      --pidfile /tmp/$APP_NAME.pid \
                      --make-pidfile \
                      --chuid $APP_USER \
                      --chdir $APP_PATH \
                      --startas rotarygame.py
    echo "$APP_NAME now running."
    ;;
  stop)
    echo -n "Stopping $APP_NAME..."
    start-stop-daemon -o --stop --pidfile /tmp/$APP_NAME.pid
    echo "stopped"
    ;;
  force-reload|restart)
    $0 stop
    $0 start
    ;;
  *)
    echo "Use: /etc/init.d/$APP_NAME {start|stop|restart|force-reload}"
    exit 1
    ;;
esac
exit 0
                       
