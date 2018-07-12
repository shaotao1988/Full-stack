import time
import redis
import threading

def notrans(conn):
    conn.incr('notrans:')
    time.sleep(.1)
    conn.decr('notrans:')

def trans(conn):
    pipeline = conn.pipeline()
    pipeline.incr('trans:')
    time.sleep(.1)
    pipeline.incr('trans:', -1)
    pipeline.execute()

if __name__ == "__main__":
    conn = redis.Redis()
    conn.delete('notrans:')
    for i in range(20):
        threading.Thread(target = notrans, args = (conn,)).start()
    time.sleep(2)
    print(conn.get('notrans:'))

    conn.delete('trans:')
    for i in range(20):
        threading.Thread(target = trans, args = (conn,)).start()
    time.sleep(2)
    print(conn.get('trans:'))
    