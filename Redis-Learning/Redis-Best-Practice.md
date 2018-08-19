# Redis最佳实践

## 作为index

- 使用sorted set做index
  ```
  ZRANGE
  ZRANGEBYSCORE
  ```
  >当score全为0时，会根据条目的字母顺序排序
- 以经纬度排序
  GEO命令可以处理经纬度相关的数据
  
  GEOADD将经纬度通过geohash算法hash成为一串数字，并且当2个点坐标相近时，被映射成的数字的前面部分完全相同，只有后面部分不同。GEO命令以ZSET类型来存储经纬度信息。
  ```
  GEOADD
  GEODIST
  GEORADIUS
  GEORADIUSBYMEMBER
  ```
- SET实现搜索
  将文档index和反index后存储到SET数据结构中，可以通过如下命令来实现简单的搜索功能
  ```
  SINTER # 同时包含某些关键字
  SUNION # 包含任一关键字
  ```

## Commmunication

- 消息队列
  LIST数据结构可以作为轻量消息队列，可以很容易地从LIST的一端存入消息，从另一端读出消息。并且LIST支持block模式，避免客户端不停到Server上Poll。

  如果需要确认消息处理完毕才能删除，可以用BRPOPLPUSH来将取出来的消息暂存到另一个列表，当该消息处理完毕时再从该列表删除。这样的好处是当某个worker进程死掉时，可以确保另外的进程在超时后可以继续处理这条消息。
  ```
  LPUSH/RPUSH
  RPOP/LPOP
  BRPOP/BLPOP
  BRPOPLPUSH
  ```

- 分布式锁Redlock
  - 需要至少3个独立的Redis实例，以避免单点故障
  - 实例间需要频率同步，但时间可以不同步

- 发布/订阅模式
  ```
  PUBLISH
  SUBSCRIBE
  ```

## Data Storage

- JSON
  ReJSON模块为Redis增加了JSON数据类型，可以操作JSON字符串中的单个属性，而不是把整个JSON对象GET过来后再在客户端处理

## 简单的限流

利用INCR和EXPIRE，比如限制1分钟内某个资源的访问不能超过20次：
```
GET user-api-key:[current minute number]
# if the value goes beyond 20, shows error to client and exit
MULTI
    INCR user-api-key:[current minute number]
    EXPIRE user-api-key:[current minute number] 59
EXEC
```

## COUNTING

SETBIT可以按位进行操作，比如统计活跃用户数
