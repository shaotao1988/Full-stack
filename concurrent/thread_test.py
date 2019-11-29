import threading
import time
from functools import wraps

number = 0
locker = threading.Lock()

def timeit(func):
    @wraps(func)
    def wrapper(*args):
        begain = time.time()
        result = func(*args)
        end = time.time()
        print("time elapsed: {:.1f}".format(end-begain))
        return result
    return wrapper

class MyThread(threading.Thread):
    @timeit
    def run(self):
        global number
        for _ in range(1000000):
            with locker:
                number += 1
        print(number)

number1 = 0
class MyThread1(threading.Thread):
    @timeit
    def run(self):
        global number1
        for _ in range(1000000):
            number1 += 1
        print(number1)

if __name__ == '__main__':
    for _ in range(5):
        MyThread().start()
        MyThread1().start()
