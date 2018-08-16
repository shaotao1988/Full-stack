# 对Redis进行扩展

在进行扩展之前，我们需要审视应用是否可能存在如下方面的性能问题：
- 如果使用了ziplist、intset等来降低内存用量，需要检查entries配置项是否过大
- 检查是否使用了最合适的存储类型，比如treat lists like sets; 将整个hash抓取过来再在代码中排序（可能使用zset在服务器端排序更合适）
- 如果需要发送很大的对象给Redis缓存，可以考虑先压缩
- 使用pipelining减少roundtrip
- 重用Redis连接，不要每次都去创建新的连接
 
## Scaling Read：增加Slave

- 只能对Master做写操作
- 加密和压缩：如果CPU快但网络带宽小，使用压缩，如果带宽够大，可以不压缩
- 层次化Master-Slave拓扑，避免单个Master的网络带宽成为性能瓶颈

## Scaling Writes and memory capcity: Sharding

在扩展写性能之前需要审视的几件事：
- 将相互无关联的数据放到不同的Redis实例上
- 使用pipelining节省roundtrip
- 在使用WATCH/MULTI/EXEC时，保证WATCH的范围不要太大，否则应考虑使用自定义的更精细的分布式锁
- 如果使用了AOF，需要保证足够的硬盘空间

Presharding for growth: 为未来扩容预留shards，开始可以将多个shards运行在同一台服务器上的多个Redis实例上，或者一个Redis的多个库中。有多个Redis实例时需要保证它们配置不同的端口和snapshot、AOF文件路径。

```python
REDIS_CONNECTIONS = {}

def get_redis_connection(component, wait = 1):
    key = 'config:reids:' + component
    old_config = CONFIGS.get(key, object()) # 从配置文件获取老配置
    config = get_config(config_connection, 'redis', component, wait) # Redis服务器获取新配置

    if config != old_config:
        CONFIGS.set(key, config)
        REDIS_CONNECTIONS[key] = redis.Redis(**config) # 创建新连接并保存
    
    return REDIS_CONNECTIONS[key]

def get_sharded_connection(component, key, shard_count, wait):
    shard = shard_key(component, 'x'+str(key), shard_count, 2)
    return get_redis_connection(shard, wait)

def sharded_connection(component, shard_count, wait = 1):
    def wrapper(function):
        @functools.wraps(function)
        def call(conn, key, *args, **kwargs):
            conn = get_sharded_connection(component, key, shard_count, wait)
            return function(conn, key, *args, **kwargs)
        return call
    return wrapper

@sharded_connection('unique', 16)
def count_visit(conn, session_id):
    ...
    if shard_add(conn, key, id, expected, SHARD_SIZE):
        conn.incr(key)
```