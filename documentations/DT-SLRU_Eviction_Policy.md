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

### 3. LIRS Policy (`LIRSCache`)
Advanced policy with bait items in [`eviction_policies.py`](BCacheSim/cachesim/eviction_policies.py:508-629):

```python
class LIRSCache(EvictionPolicy):
    def __init__(self, evictions_log, num_elems, bait_factor, ap):
        super().__init__(evictions_log, num_elems)
        self.cache = OrderedDict()
        self.num_baits = 0
        self.num_vals = 0
        self.bait_factor = bait_factor
```


## DT-SLRU Architecture

### Core Concepts

DT-SLRU divides the cache into two segments:
1. **Protected Segment**: Recently accessed items (hot)
2. **Probationary Segment**: Items that haven't been accessed recently (cold)

The key innovation is the **dynamic threshold** that controls the size ratio between these segments based on:
- Access frequency patterns
- Hit rate observations
- Temporal locality characteristics

### Proposed DT-SLRU Implementation

Based on the existing BCacheSim architecture, here's how DT-SLRU could be implemented:

```python
class DTSegmentedLRUPolicy(EvictionImpl):
    def __init__(self, cache_size, protected_ratio=0.8, adaptation_interval=1000):
        self.protected_segment = OrderedDict()  # Hot items
        self.probationary_segment = OrderedDict()  # Cold items
        self.cache_size = cache_size
        self.protected_ratio = protected_ratio
        self.protected_max = int(cache_size * protected_ratio)
        self.adaptation_interval = adaptation_interval
        self.access_count = 0
        self.hit_count = 0
        self.items = {}  # Unified view for compatibility
    
    def admit(self, key, item):
        # New items go to probationary segment
        self.probationary_segment[key] = item
        self.items[key] = item
        self._maintain_size()
    
    def touch(self, key):
        # Move from probationary to protected on access
        if key in self.probationary_segment:
            item = self.probationary_segment.pop(key)
            self.protected_segment[key] = item
        elif key in self.protected_segment:
            # Update access time in protected segment
            self.protected_segment.move_to_end(key)
        
        self.access_count += 1
        if self.access_count % self.adaptation_interval == 0:
            self._adapt_threshold()
    
    def evict(self, key=None):
        if key:
            # Specific eviction
            if key in self.protected_segment:
                item = self.protected_segment.pop(key)
            else:
                item = self.probationary_segment.pop(key)
            del self.items[key]
            return key, item
        else:
            # Choose victim based on segments
            if len(self.probationary_segment) > 0:
                # Evict from probationary first
                key, item = self.probationary_segment.popitem(last=False)
            else:
                # Fall back to protected segment
                key, item = self.protected_segment.popitem(last=False)
            del self.items[key]
            return key, item
    
    def _maintain_size(self):
        total_size = len(self.protected_segment) + len(self.probationary_segment)
        if total_size > self.cache_size:
            # Adjust protected segment size
            current_protected = len(self.protected_segment)
            if current_protected > self.protected_max:
                # Move excess from protected to probationary
                excess = current_protected - self.protected_max
                for _ in range(excess):
                    if len(self.protected_segment) > 0:
                        key, item = self.protected_segment.popitem(last=False)
                        self.probationary_segment[key] = item
            
            # Evict from probationary if still over capacity
            while len(self.protected_segment) + len(self.probationary_segment) > self.cache_size:
                if len(self.probationary_segment) > 0:
                    self.probationary_segment.popitem(last=False)
                else:
                    self.protected_segment.popitem(last=False)
    
    def _adapt_threshold(self):
        # Dynamic threshold adaptation based on hit rate
        recent_hit_rate = self.hit_count / self.adaptation_interval if self.access_count > 0 else 0
        
        if recent_hit_rate < 0.5:
            # Low hit rate - increase protected segment
            self.protected_ratio = min(0.9, self.protected_ratio + 0.05)
        elif recent_hit_rate > 0.8:
            # High hit rate - decrease protected segment
            self.protected_ratio = max(0.5, self.protected_ratio - 0.05)
        
        self.protected_max = int(self.cache_size * self.protected_ratio)
        self.hit_count = 0  # Reset counter
    
    def victim(self):
        if len(self.probationary_segment) > 0:
            return next(iter(self.probationary_segment))
        elif len(self.protected_segment) > 0:
            return next(iter(self.protected_segment))
        return None
```
