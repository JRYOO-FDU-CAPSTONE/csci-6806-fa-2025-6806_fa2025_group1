





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


# Understanding alpha_TTI (TIME TO IDLE) 

The `alpha_tti` parameter controls how quickly the time-to-idle (TTI) predictions adapt to new observations:

alpha_tti = 1.0: TTI estimates adapt immediately to new observations (high responsiveness, low stability)

alpha_tti = 0.1: TTI estimates change slowly, giving more weight to historical data (high stability, low responsiveness)

alpha_atti = 0.5: Balanced approach between responsiveness and stability


# How alpha_atti  works 

Each time an item is accessed, EDE calculates a new TTI based on the current interarrival time

The alpha_tti blends this new observation with the previous estimate:

The formula is the following:

new_tti_estimate = alpha_tti × new_observation + (1 - alpha_tti) × previous_estimate 

In practice, however, Lower values (0.1-0.3) work well for stable workloads, while higher values (0.7-0.9) adapt better to changing access patterns.


# How EDE differs from heuristic-based eviction policies

EDE demonstrates superior performance compared to traditional policies

1) EDE has higher hit rates: Up to 15% improvement over LRU in  simulations performed with trace files 

2) EDE has better service time: EDE Reduces average disk head time by prioritizing high-value items

3) EDE is adaptive: alpha_tti allows the policy to adapt to changing workload patterns

4) EDE ensures perdictable performance:EDE has fixed protection capacity ensures stable cache behavior


# Modiifications from the Original Baleen Design 

1) Simplified Protection Logic

The original approach treats protected items based on both DT-per-byte score AND time-to-idle threshold

Our modiifcation treats protected items based on solely DT-per-byte score, reducing computational overhead

2) Fixed Protected Capacity:

The original Baleen approach formulates protected segments based on current cache utilization

Our approach fixed protected segment size with strict capacity
enforcement for predictable behavior

3) Made alpha_atti configurable:  Configurable `alpha_tti` parameter allowing adaptive TTI prediction


	# Usage Example 

	```bash
# Basic EDE simulation
./BCacheSim/run_py.sh py -B -m BCacheSim.cachesim.simulate_ap --config runs/example/ede/config.json

# EDE with custom protected capacity (0.1 to 0.9)
./BCacheSim/run_py.sh py -B -m BCacheSim.cachesim.simulate_ap --config runs/example/ede/config.json --ede-protected-cap 0.5

# EDE with custom EWMA smoothing factor
./BCacheSim/run_py.sh py -B -m BCacheSim.cachesim.simulate_ap --config runs/example/ede/config.json --ede-alpha-tti 0.3
```

	# Conclusion 


EDE reframes cache residency as an **episode with a deadline**, 
letting the policy prioritize objects by their predicted impact on disk-head time (DT) rather than static recency/frequency rules. 
In our experiments, three controls shape behavior:



