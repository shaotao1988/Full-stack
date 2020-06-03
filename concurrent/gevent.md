
# 同步和异步

并发的核心思想是一项大的任务可以被分解为若干个小的子任务，这些子任务可以"同时"异步执行，而不是逐个同步执行。

这里的"同时"不是严格意义的并发。gevent是在某个greenlet进行IO等情况下，CPU空闲时，自动切换到另一个greenlet，但是在内核态始终只有一个进程在执行，区别于```multiprocessing```和```threading```模块。

gevent可以极大提升网络和IO类应用程序的性能，当某个greenlet在进行网络或IO操作时，gevent能自动识别并切换到其他greenlet执行。一个greenlet被称为一个```协程```。

```python
import gevent.monkey
gevent.monkey.patch_socket()

import gevent
import urllib.request
import time

start = time.time()
tic = lambda: "{:0.1f} seconds".format(time.time()-start)

def task(pid):
    urllib.request.urlopen('http://www.baidu.com')
    print('Task {} done at {}'.format(pid, tic()))

def synch():
    for i in range(10):
        task(i)

def asynch():
    threads = [gevent.spawn(task, i) for i in range(10)]
    gevent.joinall(threads)

if __name__ == '__main__':
    asynch()
    start = time.time()
    synch()

"""
Task 2 done at 0.4 seconds
Task 4 done at 0.4 seconds
Task 9 done at 0.4 seconds
Task 0 done at 0.4 seconds
Task 1 done at 0.5 seconds
Task 6 done at 0.6 seconds
Task 7 done at 0.6 seconds
Task 8 done at 0.6 seconds
Task 5 done at 0.6 seconds
Task 3 done at 1.1 seconds

Task 0 done at 0.1 seconds
Task 1 done at 0.3 seconds
Task 2 done at 0.7 seconds
Task 3 done at 1.1 seconds
Task 4 done at 1.5 seconds
Task 5 done at 3.1 seconds
Task 6 done at 3.4 seconds
Task 7 done at 3.7 seconds
Task 8 done at 5.1 seconds
Task 9 done at 5.4 seconds
"""
```

```gevent.spawn```将指定函数包装成greenlet线程，这些线程保存在threads数组中，然后传递给```gevent.joinall```函数，该函数会阻塞当前进程，并运行传递过来的所有greenlets线程，只有所有greenlets线程结束运行后当前进程才会往下执行。

从上面的结果可以看到，将程序运行10次，同步版本需要5.4秒，而使用gevent的异步版本只需要1.1秒，因为gevent版本的10个greenlets基本是并发执行的。

# 事件循环

上面的例子中，`urllib.request.urlopen`默认会阻塞当前线程，直到获取到远端数据，所以多次调用这个接口时会串行执行。

但是我们通过在代码起始部分调用gevent.monkey.patch_socket()，将标准库的socket变成了gevent实现的非阻塞版本。

gevent的实现是基于`event`事件机制的，当遇到阻塞操作时，gevent向操作系统注册一个事件，该阻塞操作完成后（比如socket有数据到达而变为可读状态），操作系统向gevent发送该事件，将对应的greenlet唤醒。

注册事件后，gevent马上切换到下一个greenlet执行，它可能是是之前被阻塞，但是已经收到了阻塞操作完成事件通知的另一个greenlet。

注册事件，并在它们ready后作出反应，该过程不停重复，构成gevent的`事件循环`。

需要注意的是，除非greenlet主动调用阻塞函数释放控制权，其它greenlet是无法得到执行的，所以在程序设计时需要关注是否有大量CPU计算的工作，避免饿死其它greenlet。

在gevent中，维护事件循环的是一个特殊的greenlet，它是`gevent.hub.Hub`的一个实例，下面将这个实例统称为Hub。

当应用程序发起阻塞调用时(比如上面例子中的`urllib.request.urlopen`)，当前运行的greenlet会主动切换到Hub(将控制权交给Hub)，Hub将完成事件注册和下一个greenlet切换等操作。如果此时Hub实例还未生成，则自动生成一个。

gevent的事件循环默认使用当前操作系统下的最优polling机制。

**每个操作系统线程都会有自己的Hub，可以在不同线程中使用gevent阻塞调用。**


# Monkey Patching

上一节讲到，Python的`协程`是在用户空间内，由用户线程自己接管阻塞操作，做各个协程的调度.

那么如何接管已有标准库中的阻塞调用呢？那么`Monkey Patching`就派上用场了。`Monkey Patching`模块实现了标准库中大部分阻塞调用的非阻塞版本，通过在应用初始化时调用对应的patch函数(主要是`patch_all()`)，使得其它模块在无感知情况下自动实现多协程运行。

Patching需要在程序生命周期中尽早执行，最好是在其它所有import语句前执行，并且应该在程序的主线程中执行，子线程在Patching完毕之后才能生成。
```python
from gevent import monkey
monkey.patch_all()
```

# 生成新的greenlet

gevent提供一些借口用于初始化新的greenlet，一些常见模式如下。

```python
import gevent
from gevent import Greenlet

def foo(message, n):
    
```

# Greenlet状态

- ```started```  Boolean，表示greenlet是否被启动，当gevent.spawn完成后即为started

- ```ready()```  Boolean，表示进程被halt

- ```successful()```  Boolean，表示进程被halt，且没有抛出任何异常

- ```value```  greenlet进程的返回值，可以是任意值

- ```exception```  greenlet进程抛出的异常

需要注意的是，greenlet进程中抛出的异常不会直接传递到父进程中，因此在父进程中使用```try...except...```的话，except语句是永远无法执行到的。如果需要继续在父进程中抛出异常，可以使用```raise(greenlet_thread.exception)```显式抛出。

# 进程退出

当父进程收到```SIGQUIT```信号时，如果greenlet还未执行完，则greenlet会变成僵尸进程。

常用模式是在父进程中监听SIGQUIT信号，在父进程退出前调用gevent.kill()来结束所有未完成的greenlets。

```python
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
```

也可以在run_forever的while循环中增加全局的控制变量_quit，为True时主动退出，在主进程接收到信号时，将_quit设置为True，这样可以不打断各个greenlets的工作逻辑，保证正常退出。



