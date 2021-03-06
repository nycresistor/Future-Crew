#!/bin/sh

APP_NAME="invasion"
APP_PATH="/home/pi/Future-Crew/consoles/VidEditConsole"
APP_USER=pi

case "$1" in
  start)
    echo -n "Starting $APP_NAME..."
    start-stop-daemon --start \
                      --background \
                      --pidfile /tmp/$APP_NAME.pid \
                      --chuid $APP_USER \
                      --chdir $APP_PATH \
                      --exec invasion.sh
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
    echo "Use: /etc/init.d/invasion {start|stop|restart|force-reload}"
    exit 1
    ;;
esac
exit 0
                       
