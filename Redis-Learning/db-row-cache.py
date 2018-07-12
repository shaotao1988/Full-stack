
import time
import json

'''
'delay:'             : A sorted set that stores row_id which need to be cached
                       score is the update frequency(unit: ms) of cache
'schedule:'          : A sorted set that stores the row_id which need to be cached
                       score is the next update time, if it's less than current time, 
                       the cached data in inventory:<row_id> should be updated immediately
'inventory:<row_id>' : A hash table that stores the row fetched from database as cache
'''

def schedule_row_cache(conn, row_id, delay):
    '''
    put one row from database to cache
    row_id  :  the id in the database to be cached
    delay   :  refresh frequency for the data, <=0 means don't cache any more
    '''
    conn.zadd('delay:', row_id, delay)
    conn.zadd('schedule:', row_id, time.time())

QUIT = False

def cache_row(conn):
    '''
    A deamon function that keeps monitoring the 'delay:' and 'schedule:' for every 50ms,
    and update or delete the cached data in 'inventory:<row_id>'
    '''
    while not QUIT:
        # Fetch the first item in sorted set with score(timestamp), as a list of tuples with zero or one item
        next = conn.zrange('schedule:', 0, 0, withscore = True)
        now = time.time()

        # no item in the set or it's not time for update
        if not next or next[0][1] > now:
            time.sleep(0.05)
            continue
        
        row_id = next[0][0]
        delay = conn.zscore('delay:', row_id)
        # delete the related item if delay is set to 0 or negative
        if delay <= 0:
            conn.zrem('delay:', row_id)
            conn.zrem('schedule:', row_id)
            conn.delete('inv:' + row_id)
            continue

        # update cache, and update the next updating time in 'schedule:'
        row = Inventory.get(row_id)
        conn.set('inv:' + row_id, json.dumps(row))
        conn.zadd('schedule:' + row_id, now + delay)

class Inventory(object):
    
    @classmethod
    def get(self, row_id):
        return {}