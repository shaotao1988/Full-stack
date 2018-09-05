# Scalability

> A service is said to be scalable if when we increase the resources in a system, it results in increased performance in a manner proportional to resources added.

Increasing performance in general means serving more units of work, but it can also be to handle larger units of work, for example when datasets grow.

## Web Server

Every server contains exactly the same codebase and does not store any user-related data, like sessions, on local disc and memory.

Sessions need to be stored in a centralized data store which is accessible to all your application servers.

## Database

web服务器通过水平扩展解决了大并发访问的问题，但是压力会传递到数据库，导致越来越慢并最终宕机。

2 paths:

- Stick with relational database, and do master-slave replication
  
  - Read from slaves, write to master. Vertically scale master, add more memory.

  - Sharding, SQL tuning

  - Split to multiple table, or even multiple databases

- No more joins in database query, switch to NoSQL or stay with MySQL but use it like a NoSQL database.

  - Joins need to done in application code

  - Split to multiple table, or even multiple databases

Again, database will get slower and slower as traffic grows.

## Cache

Add a cache layer between your application and data storage.

2 patterns of caching:

- Cache database queries

  - Whenever you do a query in database, you store the result dataset to cache.

  - Use hashed version of your query as cache key

  - Check cache before running query to database

  - Issue: Cache expiration. When one piece of data changes(for example a table cell), you need to delete all cached queries who may include that table cell.
  
- Cache Objects

  - Let your class assemble a dataset from your database and then store the complete instance of the class or the assembled dataset in the cache.

  - Easily get rid of the object whenever something did change, make code faster and more logical.

## Asynchronism

Improve througput and user experience

Two ways of asynchronism:

- Pre-processing
  
  - Doing time-consuming work in advance, and serving the finished result with a low request time.

  - Eg, turn dynamic content into static content. The pre-processing may be done in a timely manner, which may cause latency for data changes.

- Message queue
  
  - Jobs are queued on server, and return imediately to client. Client will be notified when job is done.

  - RabbitMQ, ActiveMQ

