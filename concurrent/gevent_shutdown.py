import gevent
import signal

def run_forever():
    while True:
        gevent.sleep(1)

def sigquit_handler():
    print('sigquit received')
    global thread
    gevent.kill(thread)

gevent.signal(signal.SIGQUIT, sigquit_handler)
thread = gevent.spawn(run_forever)
thread.join()
print("terminated")
