from future_client import FutureClient
import time

if __name__ == '__main__':
    fc = FutureClient('ws://localhost:8888/socket','client2.py w/ lib')
    print "Start pings..."
    for i in range(10):
        fc.update()
        time.sleep(0.2)

    print "Stop pings..."

    # two seconds in server should hang up on you
    time.sleep(4)

    print "Manual stop."
    fc.quit()



