import threading
from functools import wraps

class Singleton():
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance
    
class LazySingleton():
    def __init__(self):
        if not hasattr(LazySingleton, '_instance'):
            print('Instance not created.')
        else:
            print('Instance created:', self.get_instance())
    
    @classmethod
    def get_instance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = LazySingleton()
        return cls._instance

def SingletonDec(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]
    
    return _singleton

@SingletonDec
class A():
    a = 1

    def __init__(self, x=0):
        self.x = x

def synchronized(func):
    func.__lock__ = threading.Lock()

    @wraps(func)
    def lock_func(*args, **kargs):
        with func.__lock__:
            return func(*args, **kargs)
    return lock_func

class ThreadSafeSingleton():
    @synchronized
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance 

class ThreadSafeSingleton1():
    __lock__ = threading.Lock()
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            with ThreadSafeSingleton1.__lock__:
                if not hasattr(cls, '_instance'):
                    cls._instance = super().__new__(cls)
        return cls._instance 

if __name__ == "__main__":
    s1 = Singleton()
    s2 = Singleton()
    print("s1:", s1)
    print("s2:", s2)

    ls = LazySingleton()
    print(LazySingleton.get_instance())
    ls = LazySingleton()

    ts1 = ThreadSafeSingleton1()
    ts2 = ThreadSafeSingleton1()
    print("ts1:", ts1)
    print("ts2:", ts2)

    a1 = A(2)
    a2 = A(3)
    print('a1', a1, a1.x)
    print('a2', a2, a2.x)
