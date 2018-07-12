# Replication

Replication is a method by which other servers receive a continuously updated copy of the data as it's been written, so that the replicas can service read queries.

## Master/Slave

With a master/slave setup, instead of connecting to the master for reading data, clients will connect to one of the slaves to read their data(typically choosing them in a random fashion to try to balance the load).

When a slave connects to the master, the master will start a BGSAVE operation, and sends that to the slave.

Configure replication on the master side: Just ensure that the path and filename listed under the dir and dbfilename configuration options are a path and file that are writable by the Redis process.

Configure replication on the slave side: slaveof host port

>When a slave initially connects to a master, any data that had been in memory will be lost, to be replaced by the adata coming from the master.

在BGSAVE命令执行完成前，如果有新的client出现，这些新的client都将使用刚刚生成的rdb文件；如果新的client连接发生在BGSAVE命令执行完成后，将会生成新的rdb文件并同步。

## Master/Slave Chain

When one master has more than a handful of slaves, some networks are unable to keep up, especially when replication is being performed over the internet or between data centers. On the other hand, when multiple slaves connect at the same time, the outgoing bandwidth used to synchronize all of the slaves initially may cause other commands to have difficulty getting through, and could cause general network slowdowns for other devices on the same network.

As load continues to increase, we can run into situations where the single master can’t write to all of its slaves fast enough, or is overloaded with slaves reconnecting and resyncing. To alleviate such issues, we may want to set up a layer of intermediate Redis master/slave nodes that can help with replication duties.

## Handle System Failures

- Verifying snapshots and append-only files
```
redis-check-aof [--fix] <file.aof>
redis-check-dump <dump.rdb>
```
