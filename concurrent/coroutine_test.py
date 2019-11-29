import gevent

def foo():
    print("Running in foo")
    gevent.sleep(0)
    print("Explict context switch to foo again")

def bar():
    print("Explict context switch to bar")
    gevent.sleep(0)
    print("Implict context switch back to bar")

import gevent.monkey
gevent.monkey.patch_socket()

import gevent
import urllib.request
import time

start = time.time()
tic = lambda: "{:0.1f} seconds".format(time.time()-start)

def task(pid):
    urllib.request.urlopen('http://www.google.com')
    print('Task {} done at {}'.format(pid, tic()))

def synch():
    for i in range(10):
        task(i)

def asynch():
    threads = [gevent.spawn(task, i) for i in range(10)]
    gevent.joinall(threads)

if __name__ == '__main__':
    print('Case1:')
    gevent.joinall([gevent.spawn(foo),
                gevent.spawn(bar)])

    print('Case2:')
    asynch()
    start = time.time()
    synch()
