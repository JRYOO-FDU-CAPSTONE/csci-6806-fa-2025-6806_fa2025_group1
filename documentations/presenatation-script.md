
# Ablation Study Overview

I'll present our ablation study where we analyzed how sensitive Baleen's performance is to its three key parameters

# Cache Size Sensitivity

First, we varied the cache size from 100 to 500 gigabytes.

The DT-SLRU policy shows an interesting anomaly—there's a sharp spike in disk time at 384 gigabytes. 

This is likely due to a capacity threshold where certain large objects start getting evicted prematurely. 

Performance is relatively stable from 100 to 300 gigabytes and again from 400 to 500 gigabytes.



