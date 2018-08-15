# Distributed locking

Operating system-level lock: known by threads in the same process, or processes on the same machine.

Distributed lock: Clients want to have exclusive access to data stored on Redis server, so clients need to use lock defined in a scope that all clients can see, ie a lock on the Redis server.

Redis提供的锁机制：  
```
WATCH xxx
MULTI
commands to be protected by lock
EXEC
```

问题： WATCH只能针对key使用，而不能针对复杂数据结构中单独的属性使用。比如如果要锁hash结构中的某个键值对，需要对整个hash加锁，而不能对这个键值对加锁。这就相当于只能锁整张表，而不能锁某一行数据。数据并发比较大时会导致overload不停重试。

解决办法：使用setnx命令实现锁操作（set a value if the key doesn't exist）

自己实现锁时需要解决的一些异常场景：
- 某个客户端获取锁后被死锁，或者客户端挂掉，或者占用锁时间过长。需要对获取的锁加时延，时延到期后自动删除。
- A客户端获取锁，处理时间过长，它获取的锁已经超时，锁此时已被另外的客户端B获取。A会将B获取到的锁异常删除，而B对此并不知情。
- 当多个客户端同时获取锁的时候，要保证有且只有一个客户端能获取到锁。

关键点：
- 使用唯一ID作为值，这样当去删除锁的时候可以检查当前的锁是否为本客户端所有
- 容错，获取锁失败时需要重试，直到超时

