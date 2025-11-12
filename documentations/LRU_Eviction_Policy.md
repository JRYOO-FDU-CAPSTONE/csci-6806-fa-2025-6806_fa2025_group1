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

