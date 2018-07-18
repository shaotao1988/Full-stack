import time
from datetime import datetime
import contextlib
import uuid
import redis

@contextlib.contextmanager
def access_time(conn, context):
    start = time.time()
    yield

    delta = time.time() - start
    stats = update_stats(conn, context, 'AccessTime', delta)
    average = stats[1]/stats[0]

    pipe = conn.pipeline(True)
    pipe.zadd('slowest:AccessTime', context, average)
    # Only keeps the slowest 100 items
    pipe.zremrangebyrank('slowest:AccessTime', 0, -101)
    pipe.execute()

def process_view(conn, callback):
    with access_time(conn, request.path):
        return callback()

def update_stats(conn, context, type, value, timeout = 5):
    destination = 'stats:%s:%s' % (context, type)
    start_key = destination + ':start'
    pipe = conn.pipeline()
    end = time.time() + timeout
    while time.time() < end:
        try:
            pipe.watch(start_key)
            now = datetime.utcnow().timetuple()
            hour_start = datetime(*now[:4]).isoformat()

            # Record statistics by hour, check if it's next hour
            existing = pipe.get(start_key)
            pipe.multi()
            if existing and existing < hour_start:
                # record history data
                pipe.rename(destination, destination + ":" + hour_start)
                pipe.set(start_key, hour_start)

            tkey1 = str(uuid.uuid4())
            tkey2 = str(uuid.uuid4())
            pipe.zadd(tkey1, 'min', value)
            pipe.zadd(tkey2, 'max', value)
            pipe.zunionstore(destination, [destination, tkey1], aggregate = 'min')
            pipe.zunionstore(destination, [destination, tkey2], aggregate = 'max') 

            pipe.delete(tkey1, tkey2)
            pipe.zincrby(destination, 'count')
            pipe.zincrby(destination, 'sum', value)
            pipe.zincrby(destination, 'sumsq', value*value)

            return pipe.execute()[-3:]
        except redis.exceptions.WatchError:
            continue
        