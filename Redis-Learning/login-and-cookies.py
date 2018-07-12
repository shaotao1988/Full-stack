import time

'''
'login:'         : A hash entry that stores the token of login user
'recent:'        : A sorted set that stores the latest active time of token
'viewed:'        : A sorted set that stores the items viewed by user, with count as score
'viewed:<token>' : A sorted set that stores the latest 25 items viewed by corresponding user
'''

def check_token(conn, token):
    return conn.hget('login:', token)

def update_token(conn, token, user, item = None):
    timestamp = time.time()
    # add token for user
    conn.hset('login:', token, user)
    # store the last active time, token will be deleted after a period for unactive user
    conn.zadd('recent:', token, timestamp)
    if item:
        # store the latest 25 items viewed by the user for further analysis
        conn.zadd('viewed:' + token, item, timestamp)
        conn.zremrangebyrank('viewed:' + token, 0, -26) 
        # update with -1 so that item with index 0 is the most viewed
        conn.zincrby('viewed:', item, -1)

# for session cleanning
QUIT = False
# maximum token stored, the earliest token will be deleted if the token quantity exceeds the limit
LIMIT = 10000000

def clean_sessions(conn):
    '''
    Keep ony LIMIT tokens in memory, delete the unactive tokens
    '''
    while not QUIT:
        size = conn.zcard('recent:')

        if size <= LIMIT:
            time.sleep(1)
            continue
        
        # fetch the token IDs that should be removed
        end_index = min(size - LIMIT, 100)
        tokens = conn.zrange('recent:', 0, end_index - 1)

        session_keys = []
        for token in tokens:
            session_keys.append('viewed:' + token)
        
        conn.delete(*session_keys)
        conn.hdel('login:', *tokens)
        conn.zrem('recent:', *tokens)

def rescale_viewed(conn):
    '''
    only keep the 20000 most viewed items in memory
    update 'viewed:' entry in every 5 minutes
    for the remaining 20000 items, the viewed count is half the original value
    '''
    while not QUIT:
        conn.zremrangebyrank('viewed:', 20000, -1)
        conn.zinterstore('viewed:', {'viewed:': 0.5})
        time.sleep(300)


        