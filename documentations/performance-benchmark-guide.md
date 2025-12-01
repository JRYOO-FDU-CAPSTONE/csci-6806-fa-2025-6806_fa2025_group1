
## Overview

This guide provides comprehensive instructions for setting up, running, and analyzing performance benchmarks

for the Episode-Deadline Eviction (EDE) policy and comparative eviction policies. 

It covers experimental configuration, data collection, and 

result analysis to ensure reproducible and meaningful performance evaluations.


## Parameter Sensitivity Ranges

For comprehensive evaluation, test these parameter ranges:

| Parameter | Range | Step Size | Notes |
|-----------|--------|-----------|---------|
| `cache_size` | 1GB - 16GB | 2x scaling | Power-of-2 scaling recommended |
| `dt_per_byte_score` | 0.00001 - 0.001 | 10x scaling | Logarithmic steps |
| `protected_cap` | 0.1 - 0.9 | 0.1 | Linear steps |
| `alpha_tti` | 0.1 - 0.9 | 0.1 | Linear steps |



