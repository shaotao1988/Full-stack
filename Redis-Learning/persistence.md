# Persistence

## Snapshot

Take the data as it exists at one moment in time and writes it to disk.

How to initiate a snapshot:
- Calling BGSAVE command by any Redis client. Redis will fork and the child process will write the snapshot while the parent process continues to respond to commands.
- Calling SAVE command by any Redis client. Redis will stop responding to any commands until the snapshot completes.
- If Redis is configured with save lines, such as save 60 10000, Redis will automatically trigger a BGSAVE operation if 10,000 writes have occurred within 60 seconds since the last successful save has started. When multiple save lines are present, any time one of the rules match, a BGSAVE is triggered.  
- When Redis receives a request to shut down by the SHUTDOWN command, or it receives a standard TERM signal, Redis will perform a SAVE, blocking clients from performing any further commands, and then shut down.
- If a Redis server connects to another Redis server and issues the SYNC command to begin replication, the master Redis server will start a BGSAVE operation if one isn’t already executing or recently completed.

### Big Data

As Redis memory use grows over time, so does the time to perform a fork operation for the BGSAVE, this may cause the system to pause for periods of time, which could degrade Redis's performance to the point where it's unusable.  

While snapshots are great when we can deal with potentially substantial data loss in Redis, we can use append-only file persistence to allow Redis to keep more up-to-date information about data in memory stored on disk.

```
# Snapshot persistence options
# Redis will start a new BGSAVE when there are more than 1000 writes in any 60 second since the last BGSAVE
save 60 1000
stop-writes-on-bgsave-error no
rdbcompression yes
dbfilename dump.rdb

# AOF file persistence options
appendonly no
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Shared option, where to save the rdb or AOF file
dir ./
```

## AOF(Append-Only File)

Copying incoming writing commands to disk as they happen.

In basic terms, append-only file keeps a record of data changes that occur by writing each change to the end of the log file. In doing this, anyone could recover the entire dataset by replaying the append-only log from the beginning to the end.

Dark side:
- Large file
- Take long time to start up when handling large AOF file

To solve the growing AOF problem, we can use BGREWRITEAOF, wihch will rewrite the AOF to be as short as possible by removing redundant commands.

BGREWRITEAOP worsk similarly to the snapshot BGSAVE: performing a fork and subsequently rewriting the append-only log in the child.