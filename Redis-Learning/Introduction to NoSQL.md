# NoSQL 简介

## 数据库的历史

1. 关系型数据库

起源于80年代中期

优点：
- 数据持久
- SQL
- 事务
- Integration，集成

缺点：
- Impedance mismatch: 用户界面的数据往往分散在不同的数据表中，需要在多个数据表中进行联合查询，再在内存中组装成所需要的格式
- ORM层: Object Relational Mapping

2. 对象数据库

90年代中期

将内存中的对象直接存储到数据库中，无需ORM

关系型数据库已被大量用于各种系统的集成中，其它类型数据库很难有一席之地

3. NoSQL

21世纪初：互联网、大数据爆发
- Scaling：Large clusters with little boxes.数据被分片、分散存储到多个物理机器上
- SQL: Single system with big box. SQL不能很好地适应数据库集群

Google、Amazon分别开发了自己的数据存储系统Bigtable和Dynamo，并在刊物上分享他们的Idea，从而引发了NoSQL运动。

在伦敦的Johan Oskarsson准备在旧金山组织一次会议，就新出现的数据库ideas进行讨论。当时召集与会人最快捷的方式就是在Twitter上创建一个hashtag，这个tag需要简短、唯一，于是有人提出用nosql。

## NoSQL

**特点**
- Non-relational
- Open-source
- Cluster-friendly
- Schema-less
- 21st Century Web

**分类**
- Document: MongoDB, Raven DB, CouchDB
- Column-family: Cassandra, HBASE
- Graph: Neo4j
- Key-Value: Redis, riak

**Data Models**

    Common feature: No schema. 可以以复杂的数据结构为单元进行存储(**Aggregate oriented**)
- Key Value
  Hashmap结构，数据库对Value的值一无所知，也不能基于Value进行任何操作（查找、排序等）
- Document
  存储的是复杂的数据结构，一般被封装为JSON格式，可以部分地查询或更新文档数据结构. eg:
  {
      "id": 1001,
      "customer_id": 1234,
      "line-items":[
          {"product_id": 4555, "quantity": 8},
          {"product_id": 7845, "quantity": 12},
          {"product_id": 8432, "quantity": 40}
      ]
  }
- Column-family
  一个条目row key可以存储多个column-family，每个column-family又是多个column key和column value的组合. eg：
  1234(row key)
    profile(Column-family 1)
        name: Martin(column key-values)
        biliingAddress: data...
        payment: data...
    orders(Column-family 2)
        OR1001: data...
        OR1002: data...
- Graph
  很方便的做节点之间的关联分析，不是Aggregate oriented。

>NoSQL的优势：数据分片后，关系型数据库需要到每个分片中做数据查询，再通过应用程序Aggregate后返回给客户端，而NoSQL只需要到对应的数据分片上查询一次就可以了

>NoSQL的劣势：如果需要对上面的line-item数据做以Product_id为维度的聚合分析会非常复杂，通常需要以类似Map-Reduce的方式来处理，而关系型数据库则可以很方便的处理这样的分析

**NoSQL数据库的一致性**

事务可以保证数据库数据的一致性。相对于关系型数据库，NoSQL数据库对事务的依赖程度没那么高，因为数据已经被聚合在一起了，可以对数据加版本号来防止并发操作时的数据一致性问题（乐观锁）。

逻辑一致性：ACID中的C. 数据可以在一台机器上，也可以通过sharding分布在多台机器上。

复制一致性：数据库读写分离时，Master和Slave之间数据的一致性。

>CAP理论: Consistency, Availability, Partition Tolerance只能二者选其一

这里的availability指的是提供服务的能力，不是通常意义上服务器宕机导致的资源不可用

举例：在Expedia上预订房间，Expedia在世界不同地方建立了数据中心（对网络、数据等Partition），假设区域A和区域B之间的网络完全中断，这时Amazon有2种选择：
- 选择可用性但是放弃一致性：继续为用户提供预订服务，但是可能存在区域A、B的2个不同的用户预订了同一个房间的情况
- 选择一致性但是放弃可用性：提示用户服务不可用

**为什么用NoSQL**

1. 快速开发
   没有Impedance mismatch问题，数据库模型跟对象模型完全一致，不用维护关系数据库中各种表之间复杂的关系，缩短产品上线时间。
2. 大数据分析
   NoSQL天生具有很好的Scaling特性，可以配合Map-Reduce进行超大规模数据的存储和分析。
