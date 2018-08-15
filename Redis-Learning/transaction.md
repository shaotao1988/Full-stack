# Transaction

- Prevent data corruption  
    Read-Check-Write has problem in concurrent environment
- Improve performance
    Delaying execution of commands until EXEC is called when using MULTI/EXEC, the client will hold off until all of the commands are known. So the client will send the MULTI, followed by the series of commands to be executed, and end with EXEC, all at the same time(pipelining), which can reduce the number of network round trips that a client needs to wait for.

A typical skeleton for transaction is:

```python
pipe = conn.pipeline()
while time.time() < end:
    try:
        pipe.watch(...)
        # do some preparing and checking
        ...
        if ...:
            pipe.unwatch()
            return False

        pipe.multi()
        ...
        pipe.execute()
        return True
    except redis.exceptions.WatchError:
        # don't do anything, retry
        pass
return False
```

Problem: Simple transaction doesn't actually do anything until EXEC is called, which means that we can't use data we read to make decisions until after we may have needed it.

## Non-transactional pipelines

In many cases, we just want to execute multiple commands, these commands don't need to be transactional, we can use non-transactional pipelines to pack these command and get the result with less round trips to server.

Non-transactional pipeline can reduce the number of round trips by a factor of 3-5.

```python
pipe = conn.pipeline(False)
```

## Performance considerations

Running redis-benchmark will give us the performance characteristic of the server and of Redis.

Compared to redis-benchmark running with a single client, we can expect the Python Redis client to perform at roughly 50–60% of what redis-benchmark will tell us for a single client and for non- pipelined commands, depending on the complexity of the command to call.

One common cause for low performance is that we are connecting for every command/group of commands. We should reuse Redis connections.
