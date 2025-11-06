# DT-SLRU Eviction Policy Implementation in BCacheSim

## Overview

DT-SLRU (Dynamic Threshold Segmented LRU) is an advanced cache eviction policy that extends the traditional Segmented LRU (SLRU) by incorporating dynamic threshold adjustment based on access patterns. While DT-SLRU is not explicitly implemented in the current BCacheSim codebase, this document explains how it could be implemented based on the existing eviction policy architecture.

## Current Eviction Policies in BCacheSim

### 1. LRU Policy (`LRUPolicy`)
The basic LRU implementation in [`eviction_policies.py`](BCacheSim/cachesim/eviction_policies.py:140-161):

```python
class LRUPolicy(EvictionImpl):
    def __init__(self):
        self.items = OrderedDict()
    
    def admit(self, key, item):
        self.items[key] = item
    
    def touch(self, key):
        # Moves to end. We evict from start.
        self.items.move_to_end(key)
    
    def evict(self, key=None):
        # pop in FIFO order, from front
        if key:
            self.items.move_to_end(key, last=False)
        return self.items.popitem(last=False)
```

### 2. TTL Policy (`TTLPolicy`)
Time-based eviction policy in [`eviction_policies.py`](BCacheSim/cachesim/eviction_policies.py:112-138):

```python
class TTLPolicy(EvictionImpl):
    def __init__(self):
        self.pqueue = pqdict.pqdict()
        self.items = {}
    
    def admit(self, key, item):
        self.items[key] = item
        self.pqueue[key] = item.ts_expire
    
    def evict(self, key):
        if key is not None:
            del self.pqueue[key]
        else:
            key, _ = self.pqueue.popitem()
        return key, self.items.pop(key)
```


