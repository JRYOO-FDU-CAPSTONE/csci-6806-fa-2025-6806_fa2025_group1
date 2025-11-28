
# Ablation Study Overview

I'll present our ablation study where we analyzed how sensitive Baleen's performance is to its three key parameters

# Cache Size Sensitivity

First, we varied the cache size from 100 to 500 gigabytes.

The DT-SLRU policy shows an interesting anomaly—there's a sharp spike in disk time at 384 gigabytes. 

This is likely due to a capacity threshold where certain large objects start getting evicted prematurely. 

Performance is relatively stable from 100 to 300 gigabytes and again from 400 to 500 gigabytes.


# Tau DT Sensitivity

Now the most critical parameter: tau_DT. This controls the threshold for downtime prediction. 

At very low values below 0.0001, we see high churn—the system admits and evicts objects too frequently, 

causing Peak DT to spike above 31.6 milliseconds. The optimal range is 0.001 to 0.01, 

where we achieve our best Peak DT of 31.5 milliseconds and hit rate of 2.25%. 

Beyond 0.01, performance plateaus as the threshold becomes too conservative.


The curve shows dramatic non-linear behavior, which means this parameter requires careful tuning for optimal performance.


# Protected Cap Sensitivity

The PROTECTED cap parameter controls how much of the cache is reserved for protected segments.

Our results show this has minimal impact on the EDE policy—performance remains relatively flat across different values. 

This suggests that EDE's eviction strategy is robust to this particular configuration.


