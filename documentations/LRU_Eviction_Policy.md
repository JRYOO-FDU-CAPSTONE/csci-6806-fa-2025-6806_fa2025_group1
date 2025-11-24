# LRU Baseline Eviction Policy Implementation in BCacheSim

## Overview

The LRU (Least Recently Used) eviction policy serves as the baseline eviction mechanism in BCacheSim. This document provides a comprehensive explanation of how the LRU policy is implemented, its core components, and how it integrates with the broader caching system.

## Core LRU Implementation

### LRUPolicy Class

The LRU eviction policy is implemented in the [`LRUPolicy`](BCacheSim/cachesim/eviction_policies.py:195) class, which inherits from the [`EvictionImpl`](BCacheSim/cachesim/eviction_policies.py:145) base class.

```python
class LRUPolicy(EvictionImpl):
    def __init__(self):
        self.items = OrderedDict()
```

The implementation uses Python's `OrderedDict` to maintain the order of items based on their access patterns, where the most recently accessed items are kept at the end of the dictionary.

### Key Methods

#### 1. Admission (`admit`)
```python
def admit(self, key, item):
    self.items[key] = item
```
- Adds new items to the cache
- Items are automatically placed at the end of the `OrderedDict` (most recently used position)

#### 2. Access Update (`touch`)
```python
def touch(self, key):
    # Moves to end. We evict from start.
    self.items.move_to_end(key)
```
- Updates the access time of existing items
- Moves the accessed item to the end of the `OrderedDict` (most recently used position)

#### 3. Eviction (`evict`)
```python
def evict(self, key=None):
    # pop in FIFO order, from front
    if key:
        self.items.move_to_end(key, last=False)
    return self.items.popitem(last=False)
```
- Evicts the least recently used item (from the front of the `OrderedDict`)
- If a specific key is provided, moves it to the front before eviction
- Returns the evicted key-item pair

#### 4. Victim Selection (`victim`)
```python
def victim(self):
    if len(self.items) == 0:
        return None
    return next(iter(self.items))
```
- Identifies the next item to be evicted without actually removing it
- Returns the key of the least recently used item (first item in the `OrderedDict`)



## Integration with QueueCache

The LRU policy is integrated into the main caching system through the [`QueueCache`](BCacheSim/cachesim/eviction_policies.py:1091) class, which serves as the primary cache implementation.

### Cache Initialization

```python
# In QueueCache.__init__
if options.eviction_policy and options.eviction_policy.startswith("ttl"):
    self.cache = TTLPolicy()
elif options.eviction_policy and options.eviction_policy == "DT-SLRU":
    self.cache = DTSLRUPolicy(options.dt_per_byte_score)
elif options.eviction_policy and options.eviction_policy == "EDE":
    self.cache = EDEPolicy(...)
else:
    self.cache = LRUPolicy()  # Default LRU policy
```

### Cache Operations

The LRU policy is used in several key operations within `QueueCache`:

#### 1. Cache Lookup (`find`)
```python
def find(self, key, key_ts, count_as_hit=True, touch=True, check_only=False):
    found = key in self.cache
    if found and not check_only:
        if count_as_hit:
            self.cache[key].markAccessed(key_ts)
            self.bump("hits")
        elif touch:
            self.cache[key].touch(key_ts)
        
        # promote by removing and reinserting at the head.
        if self.lru:
            self.cache.touch(key)
```

#### 2. Cache Admission (`admit`)
```python
def admit(self, key, ts, *, ttl=None, ts_access=None, episode=None, **item_kwargs):
    # ... admission logic ...
    self.cache.admit(key, TTLItem(ts, key, ts_access=ts_access, ttl=ttl, episode=episode, **item_kwargs))
    
    if len(self.cache) >= self.cache_size:
        self.do_eviction(ts)
```

#### 3. Cache Eviction (`do_eviction`)
```python
def do_eviction(self, ts, key=None):
    evicted = self.cache.evict(key)
    self.block_counts[evicted[1].key[0]] -= 1
    self.dec_episode(evicted[1].key, ts)
    self.log_eviction(ts, evicted)
```


## Item Management

### QueueItem Base Class

The LRU policy works with [`QueueItem`](BCacheSim/cachesim/eviction_policies.py:25) objects that track access patterns:

```python
class QueueItem(object):
    def __init__(self, ts, key):
        self.last_access_time = ts
        self.admission_time = ts
        self.hits = 0
        self.key = key

    def touch(self, ts):
        self.last_access_time = ts

    def markAccessed(self, ts):
        self.touch(ts)
        self.hits += 1
```

### TTLItem Extension

For more advanced caching scenarios, the system uses [`TTLItem`](BCacheSim/cachesim/eviction_policies.py:78) which extends `QueueItem` with additional features like TTL (Time To Live) and service time calculations.

## Configuration and Usage

### Default Behavior

The LRU policy is the default eviction policy in BCacheSim when no specific policy is specified. It's enabled by setting the `lru=True` parameter in the `QueueCache` constructor.

### Policy Selection

The eviction policy can be configured through command-line options or configuration files:

```python
# In simulate_cache_driver
if options.lirs:
    logjson["EvictionPolicy"] = "LIRS"
elif options.fifo:
    logjson["EvictionPolicy"] = "FIFO"
else:
    logjson["EvictionPolicy"] = "LRU"  # Default
```

## Performance Characteristics

### Time Complexity
- **Admission**: O(1) - Adding to `OrderedDict`
- **Access Update**: O(1) - Moving item to end
- **Eviction**: O(1) - Removing from front
- **Victim Selection**: O(1) - Accessing first element

### Space Complexity
- **Storage**: O(n) where n is the number of cached items
- **Overhead**: Minimal - only stores key-item pairs in `OrderedDict`

## Advantages and Limitations

### Advantages
1. **Simplicity**: Straightforward implementation using standard Python data structures
2. **Efficiency**: O(1) operations for all core functions
3. **Predictability**: Well-understood behavior and performance characteristics
4. **Baseline**: Provides a reliable baseline for comparing against more complex policies

### Limitations
1. **No Frequency Awareness**: Only considers recency, not access frequency
2. **No Size Awareness**: Doesn't account for item sizes when making eviction decisions
3. **No Cost Awareness**: Doesn't consider the cost of re-fetching evicted items
4. **Scan Resistance**: Vulnerable to sequential access patterns that can pollute the cache

## Comparison with Other Policies

BCacheSim implements several eviction policies that extend or replace the basic LRU:

1. **TTL Policy**: Adds time-to-live expiration
2. **DT-SLRU**: Segmented LRU with service-time awareness
3. **EDE**: Episode-deadline eviction with predictive capabilities
4. **LIRS**: Low Inter-reference Recency Set for improved scan resistance

The LRU policy serves as the foundation and baseline against which these more sophisticated policies are compared.


These metrics are collected and reported through the [`StatsDumper`](BCacheSim/cachesim/sim_cache.py:46) class for performance analysis.