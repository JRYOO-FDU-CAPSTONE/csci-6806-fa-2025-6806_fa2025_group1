
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


## Key Metrics Collections
		

1. **Peak Disk Head Time (Peak DT)**
   - Definition: Maximum disk head time across all time windows
   - Importance: Directly correlates with storage capacity requirements
   - Collection: Automatically calculated by simulator

2. **Median Disk Head Time (Median DT)**
   - Definition: 50th percentile of disk head time distribution
   - Importance: Indicates typical system performance
   - Collection: Reported in simulation output

	
## Best Practices

1. **Start Small**: Begin with small trace samples to validate setup
2. **Document Everything**: Keep detailed logs of all experiments
3. **Version Control**: Track code and configuration changes
4. **Automate**: Use scripts for repetitive tasks
5. **Validate**: Cross-check results with known baselines
6. **Share**: Make data and analysis scripts available

3. **Hit Rate**
   - Definition: Percentage of requests served from cache
   - Importance: Traditional cache performance metric
   - Collection: Available in simulation statistics

### Secondary Metric


	4. **Byte Hit Rate**
   - Definition: Percentage of bytes served from cache
   - Importance: Indicates cache efficiency for large objects

5. **Average Response Time**
   - Definition: Mean response time across all requests
   - Importance: End-to-end performance impact

6. **Cache Utilization**
   - Definition: Percentage of cache capacity utilized
   - Importance: Resource efficiency metric

