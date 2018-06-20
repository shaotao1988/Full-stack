
# sort
SORT key [BY pattern] [LIMIT offset count] [GET pattern] [ASC|DSC] [ALPHA] [STORE destination]
```
127.0.0.1:6379> hset bug:12339 severity 3
(integer) 1
127.0.0.1:6379> hset bug:12339 priority 1
(integer) 1
127.0.0.1:6379> hset bug:12339 details '{"id": 12339, "Des": "bug 1"}'
(integer) 1
127.0.0.1:6379> hset bug:1382 severity 2
(integer) 1
127.0.0.1:6379> hset bug:1382 priority 2
(integer) 1
127.0.0.1:6379> hset bug:1382 details '{"id": 1382, "Des": "bug 2"}'
(integer) 1
127.0.0.1:6379> hset bug:338 severity 5
(integer) 1
127.0.0.1:6379> hset bug:338 priority 3
(integer) 1
127.0.0.1:6379> hset bug:338 details '{"id": 338, "Des": "bug 3"}'
(integer) 1
127.0.0.1:6379> sadd watch:Victor 12339 1382 338 
(integer) 3
127.0.0.1:6379> sort watch:Victor by bug:*->priority get bug:*->details
1) "{\"id\": 12339, \"Des\": \"bug 1\"}"
2) "{\"id\": 1382, \"Des\": \"bug 2\"}"
3) "{\"id\": 338, \"Des\": \"bug 3\"}"
127.0.0.1:6379> sort watch:Victor by bug:*->priority get bug:*->details store watch_by_priority:Victor
(integer) 3
127.0.0.1:6379> lrange watch_by_priority:Victor 0 -1
1) "{\"id\": 12339, \"Des\": \"bug 1\"}"
2) "{\"id\": 1382, \"Des\": \"bug 2\"}"
3) "{\"id\": 338, \"Des\": \"bug 3\"}"
127.0.0.1:6379> 
```

# scan
SCAN cursor [MATCH parttern] [COUNT count]
- scan can return the same key multiple times
- scan only guarantees that values which were present before the command will be returned
```
127.0.0.1:6379> scan 0 match bug:* count 2
1) "12"
2) (empty list or set)
127.0.0.1:6379> scan 12 match bug:* count 2
1) "6"
2) 1) "bug:338"
127.0.0.1:6379> scan 6 match bug:* count 2
1) "14"
2) (empty list or set)
127.0.0.1:6379> scan 14 match bug:* count 2
1) "13"
2) (empty list or set)
127.0.0.1:6379> scan 13 match bug:* count 2
1) "7"
2) 1) "bug:12339"
127.0.0.1:6379> scan 7 match bug:* count 2
1) "0"
2) 1) "bug:1382"
127.0.0.1:6379> 
```

# TRANSACTIONs
- All commands in a transaction are sequentially executed as a single isolated operation. No other commands can be executed between a transaction.
- Transaction is atomic.

```
127.0.0.1:6379> multi
OK
127.0.0.1:6379> set tutorial redis
QUEUED
127.0.0.1:6379> incr visitors
QUEUED
127.0.0.1:6379> exec
1) OK
2) (integer) 1
```
