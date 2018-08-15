# Reduce Memory Reusage

## ziplist

### Structure of linked list

- 3 pointers: to previous node, next node, the string object
- String object: two int(one for object length, one for remaining free bytes), string buffer with '\0' terminated.

Overhead: (3+2) int plus one termination byte
Waste a lot of memory if we are handling short and simple objects.

### Structure of ziplist

- length(one byte) + length(one byte) + string element
- First length: size of the previous entry(for easy scanning in both directions)
- Second length: size of current entry

### Using ziplist encoding 

Can be used for LIST, HASH and ZSET

```
list-max-ziplist-entries 512
list-max-ziplist-value 64

hash-max-ziplist-entries 512
hash-max-ziplist-value 64

zset-max-ziplist-entries 128
zset-max-ziplist-value 64
```

entries: the maximum number of items allowed  
value: how large in bytes each individual entry can be

If both the entries and value limits are met, Redis will use ziplist encoding for **LIST, HASH and ZSET**.

## intset

Default structure for SET: hashtable

intset: sorted array

- Low overhead
- Speed operation

Conditions:
- SET members can be intepreted as base-10 integers within the range of signed long integer
- SET is shorter than specified in *set-max-intset-entries*

```
set-max-intset-entries 512
```

## Sharding

- 将大数据库按照一定规则切分为若干小数据库以应对大并发量的瓶颈。
- 将大数据集切分为小数据集，使Redis可以使用ziplist和intset来降低内存用量

```
Key -> Value
Key:<shard-id> -> Value
```

**1. Sharding LIST**: 需要借助Lua脚本

**2. Sharding ZSET**: 大部分ZSET的操作都需要整个ZSET数据才能进行，比如ZRANGE, ZRANGEBYSCORE, ZRANK等，所以对ZSET进行sharding并不会获得多大的增益。

**3. Sharding HASH**

```python
'''
根据原始key生成shard_key， 如果key不是数字，就用crc32值
'''
def shard_key(base, key, total_elements, shard_size):
    if isinstance(key, (int, long)) or key.isdigit():
        shard_id = int(str(key), 10) % shard_size
    else:
        shard_size = 2 * total_elements
        shard_id = binascii.crc32(key) % shard_size
    
    return "%s:%s" % (base, shard_id)

# Sharded HSET and HGET functions
def shard_hset(conn, base, key, value, total_elements, shard_size):
    shard = shard_key(base, key, total_elements, shard_size)
    return conn.hset(shard, key, value)

def shard_hget(conn, base, key, total_elements, shard_size):
    shard = shard_key(base, key, total_elements, shard_size)
    return conn.hget(shard, key)
```

**4. Sharding SET**


