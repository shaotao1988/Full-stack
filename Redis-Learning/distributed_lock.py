import uuid
import time
import redis
import math

def acquire_lock(conn, lockname, acquire_timeout = 10, lock_timeout = 10):

    identifier = str(uuid.uuid4())
    lock_timeout = int(math.ceil(lock_timeout))
    lockname = 'lock:' + lockname

    end = time.time() + acquire_timeout
    while time.time() < end:
        if conn.setnx(lockname, identifier):
            conn.expire(lockname, lock_timeout)
            return identifier
        elif not conn.ttl(lockname):
            conn.expire(lockname, lock_timeout)
            
        time.sleep(0.001)

    return False

def release_lock(conn, lockname, identifier):
    pipe = conn.pipeline(True)
    lockname = 'lock:' + lockname

    try:
        pipe.watch(lockname)
        # need to check if it's still holding the lock
        if pipe.get(lockname) == identifier:
            pipe.multi()
            pipe.delete(lockname)
            pipe.execute()
            return True
    except redis.exceptions.WatchError:
        pass
    
    pipe.unwatch()
    return False
