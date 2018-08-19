import functools

class locker:
    def __init__(self):
        print('locker.__init__()')
    
    @staticmethod
    def acquire():
        print('locker.acquire()')
    
    @staticmethod
    def release():
        print('locker.release()')

# 带参数的装饰器
def deco(cls):
    def _deco(func):
        # 最内层的装饰函数的签名需要跟func保持一致，不然装饰完再赋值给func函数后，函数接口就发生了变化
        @functools.wraps(func) # 维持func函数内置属性，比如函数名之类的
        def __deco(*args, **kwargs):
            print('before %s called [%s]' % (func.__name__, cls))
            try:
                cls.acquire()
                return func(*args, **kwargs)
            finally:
                cls.release()
        return __deco
    return _deco

@deco(locker)
def myfunc():
    print('myfunc() called')

myfunc()
