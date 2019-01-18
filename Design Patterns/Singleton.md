
# 单例模式
单例模式是一种创建模式，它提供一种创建全局唯一对象的方法，广泛应用在日志、数据库或其他可能存在资源访问冲突的场景。

单例模式的特点为：

- 保证一个类最多只有一个对象被创建出来

- 提供对象的全局访问接口

- 一般用于共享资源的并发访问

Python的模块就是天然的单例模式，模块只有在第一次被导入时才会进行初始化，后面再导入时直接返回已经初始化的模块对象：
```python
class Singleton():
    def foo(self):
        pass

singleton = Singleton()
```

将文件命名为singleton.py，在其它文件中导入这个文件中的对象，该对象就是单例的:
```python
from mysingleton import singleton
```

## 普通单例模式

Python的魔术方法__new__用于创建对象，__init__用于初始化创建的对象，所以单例模式生成对象的控制只能在__new__中完成。

```python
class Singleton():
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance
    
if __name__ == "__main__":
    s1 = Singleton()
    s2 = Singleton()
    print("s1:", s1)
    print("s2:", s2)

"""
s1: <__main__.Singleton object at 0x1047e1be0>
s2: <__main__.Singleton object at 0x1047e1be0>
"""
```

## 懒汉模式

上面的单例创建方式中，_instance对象在实例化的时候就创建出来了，还有一种延迟创建对象的方法，即使用时通过get_instance方法创建。

需要注意的是，这种实现方式下，只有通过LazySingleton.get_instance()得到的才是单例对象，直接LazySingleton()得到的并不是单例对象。

```python
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

if __name__ == "__main__":
    ls = LazySingleton()
    print(LazySingleton.get_instance())
    ls = LazySingleton()

"""
Instance not created.
Instance not created.
<__main__.LazySingleton object at 0x10ca65518>
Instance created: <__main__.LazySingleton object at 0x10ca65518>
"""
```

## 使用装饰器的单例模式

我们可以用装饰器将类转换为单例模式

```python
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

if __name__ == "__main__":
    a1 = A(2)
    a2 = A(3)
    print('a1', a1, a1.x)
    print('a2', a2, a2.x)
"""
a1 <__main__.A object at 0x1096eeeb8> 2
a2 <__main__.A object at 0x1096eeeb8> 2 #只初始化了一次
"""
```

## 线程安全的单例模式

单例对象生成时，如果多个线程同时进入下面的if判断会得到相同的结果，会创建出多个对象，所以不是线程安全的，需要加锁保证线程安全。

```python
        ...
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        ...
```

线程安全的单例代码如下：

```python
import threading

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

if __name__ == "__main__":
    ts1 = ThreadSafeSingleton()
    ts2 = ThreadSafeSingleton()
    print("ts1:", ts1)
    print("ts2:", ts2)
```

这样比较简单粗暴，把整个__new__都锁了，存在锁粒度太大的问题。我们把锁的范围再缩小一点：

```python
import threading

class ThreadSafeSingleton1():
    __lock__ = threading.Lock()
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            with ThreadSafeSingleton1.__lock__:
                if not hasattr(cls, '_instance'):
                    cls._instance = super().__new__(cls)
        return cls._instance 
```

这里之所以不是在外层把整个if语句锁起来，而是在if内层加锁，同时采用2层判断的原因有2点：

- 直接锁外层if依然存在锁粒度太大的问题

- 每次通过ThreadSafeSingleton()或ThreadSafeSingleton.get_instance()获取单例对象的时候，都会加锁，影响性能，其实只要在第一次生成单例对象的时候才有必要加锁，一旦单例对象已经生成，就没必要加锁了
