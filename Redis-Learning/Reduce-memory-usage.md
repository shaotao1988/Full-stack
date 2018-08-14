# Reduce Memory Reusage

## **ziplist**

### Structure of linked list

- 3 pointers: to previous node, next node, the string object
- String object: two int(one for object length, one for remaining free bytes), string buffer with '\0' terminated.

Overhead: (3+2) int plus one termination byte
Waste a lot of memory if we are handling short and simple objects.

### Structure of ziplist

- length(one byte) + length(one byte) + string element
- First length: size of the previous entry(for easy scanning in both directions)
- Second length: size of current entry

## Using ziplist encoding 

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

## **intset**

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

