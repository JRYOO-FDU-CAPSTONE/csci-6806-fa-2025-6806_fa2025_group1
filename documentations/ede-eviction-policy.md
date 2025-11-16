





This document intends to be a documentation we did for the ede eviction policy.

# Overview of EDE 


The Episode-Deadline Eviction (EDE) policy is a sophisticated cache eviction strategy designed specifically for flash-based storage systems.

EDE predicts when cached items will become idle and evicts items that are closest to their predicted expiration time,

while protecting high-value items based on their service-time-per-byte (DT-per-byte) characteristics.

          # Purpose of EDE 
 		
	EDE addresses a fundamental challenge in flash caching: 

	determining which cached items are most likely to be accessed again and which can be safely evicted.

	Traditional eviction policies like LRU (Least Recently Used) make decisions based solely on recency,

	but EDE incorporates predictive modeling to anticipate future access patterns.


        # EDE's time to idle prediction 


          EDE uses episode context to predict when items will become idle. Each item's time-to-idle (TTI) is estimated based on its maximum interarrival time within its episode, with  to adapt predictions over time 
        
           In EDE, Items are evaluated based on their service-time savings per byte:
           
            This can be denoted with the following formula: 
        
           DT-per-byte = (hits × seek_time + chunks × transfer_time) / size_in_bytes

	Items exceeding a configurable DT-per-byte threshold are protected from eviction. 

	#  Protected Segment Management 
	EDE maintains a protected segment that reserves a configurable fraction of cache capacity for high-value items.
	
	This prevents high DT-per-byte items from being evicted even when their predicted idle time is approaching.

	#Key Features 
	
	**Predictive Eviction**: Evicts items closest to their predicted expiration time
- 	**Value-Based Protection**: Protects high-value items based on DT-per-byte scores
- 	**Adaptive Learning**: Uses EWMA smoothing to adapt to changing access patterns
-	 **Fixed Protection Capacity**: Ensures predictable cache behavior

	## Configuration Parameters

| Parameter | Description | Range |
|-----------|-------------|--------|
| `dt_per_byte_score` | Minimum DT-per-byte threshold for protection | seconds/byte |
| `protected_cap` | Maximum fraction of cache reserved for protected items | 0.0-1.0 |
| `alpha_tti` | given variable  for TTI updates | 0.0-1.0 |
