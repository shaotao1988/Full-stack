import time
import redis

def list_item(conn, itemid, sellerid, price):
    inventory = "inventory:%s" % sellerid
    item = "%s.%s" % (itemid, sellerid)
    pipe = conn.pipeline()

    # retry for 5s at maximum
    end = time.time() + 5
    while time.time() < end:
        try:
            pipe.watch(inventory)
            # item is not in user's inventory
            if not pipe.sismember(inventory, itemid):
                pipe.unwatch()
                return False

            pipe.multi()
            pipe.zadd("market:", item, price)
            pipe.srem(inventory, itemid)
            pipe.execute()
            return True
        except redis.exceptions.WatchError:
            # retry on watcherror
            pass
    return False

def purchase_item(conn, buyerid, sellerid, itemid, lprice):
    buyer = "user:%s" % buyerid
    seller = "user:%s" % sellerid
    inventory = "inventory:%s" % buyerid
    item = "%s.%s" % (itemid, sellerid)
    pipe = conn.pipeline()
    end = time.time() + 10

    while time.time() < end:
        try:
            # watch for marcket and buyer's account
            pipe.watch("market:", buyer)
            price = pipe.zscore("market:", item)
            funds = int(pipe.hget(buyer, 'funds')) 
            if price != lprice or price > funds:
                pipe.unwatch()
                return False
            
            pipe.multi()
            pipe.sadd(inventory, itemid)
            pipe.hincrby(seller, 'funds', price)
            pipe.hdecrby(buyer, 'funds', price)
            pipe.zrem("market:", item)
            pipe.execute()
            return True
        except redis.exceptions.WatchError:
            pass
    
    # Timeout
    return False

    