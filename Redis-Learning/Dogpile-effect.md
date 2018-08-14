# DOGPILE

## Problem

What if a cache expires and then you got hundreds of requrests at the same time? It can't be served from cache any more, so your database are hit with numerous processed trying to re-generate the value. And the more requests database receive, the slower and less responsive they get. Until eventually they likely go down.

## Preventing

Preventing dogpile effect boils down to having just one process(first one to come) regenerating new values while other subsequent processes:
- Serving the old value from cache until it's refreshed by the first process
- Waiting until the new value is regenerated

How to server old value while the cache is expired?

Cache should be given an extended life time, so they are not physically removed when they are expired and they can still be served if there is an need.

## Implementation

Using semaphore lock.

If value expires, the first process acquires a lock and starts generating new value. All the subsequent requests check if lock is acquired and serve old value. After new value is generated, lock is released.

