# BCacheSim

It is a Cache Simulator for Flash Caching in Bulk Storage. It is a specialized cache simulator designed and developed as a part of Baleen research project. It mainly focuses on optimizing flash cache performance in large scale data centers.

The simulator specifically addresses the limited write endurance of SSDs by implementing some intelligent admission and eviction policies to make the best decisions regarding which blocks of data should be written to the flash and which blocks can be discarded, based on Disk-head Time (DT) as a more accurate metric on backend utilization than the traditional hit rate metrics. The system uses a system of machine learning-based admission and prefetching policies such as the advanced Baleen algorithm, as well as traditional methods such as RejectX and CoinFlip. BCacheSim is used to process the traces of real-world applications from large-scale storage systems such as Meta's Tectonic filesystem, apply different caching policies, and generate comprehensive performance metrics such as service time utilization, service time peak analysis, IOPs saved ratios, cache hit rates, write rates, and prefetch effectiveness.

It has several key features that make it unique from the traditional cache simulators and allow for sophisticated analysis of flash caching systems. The Flash cache specially focuses on problem of hybrid architecture where SSD's are used for caching purpose, implementing Ml guided policies to optimize performance minimizing the limitation of write endurance. It uses Disk-Head Time as main parameter which is an accurate measure in terms of disk utilization which also help to predict better performance.

# Disk-Head Time

Disk-Head time is defined as time a disk spend on fulfilling the request on backend. It is one of the accurate metric for the storage system ultization than the traditional metric of hit rate and miss rate. The metric like hit rate and miss rate uses the count of hit and miss whenever there is a request for the service. Unlike this  Disk Head time calculates the total time spent on disk seek time, rotational delays and data transfer when request are served from the backend storage not from cache. 

In this BcacheSim simulator, DT is used as main parameter which is taken in account for all admission and eviction policies which aims for the minimum Peak DT instead of only maximizing hit rates. Simulator is used to observe the peak DT over different parameters so it can be analyzed properly and which can help in the study of different cache policies and their impact.

# ML-Guided Addmission Policy

Ml-Guided addmission policy is an approach made for efficient cache management using machine learning to make proper addmission and prefeteching decision to reduce Peak DT. It is very different from tradition heuristic based policies which is based on fixed threshold or rules, these Ml-guided policies are trained on episode based features to predict whether to admit the particular episode or exclude the episode so it can benefit the flash write cost. The ML-guided training is based on optimal addmission Policy (OPT) which can make addmission decisions and train ML models to utilize that optimal decision maintaing flash write constraints. 

For this ML approach episode based model is used which treats each cache residency as a single logical unit instead of whole individual block of data. It is very useful for Ml model to learn the patterns about access sequence and make decision for optimizing the episode lifecycle. Being based on these ML model is implemented by simulator which predict which block are likely to be accessed in future which enable proactive admission of data before it is requested.

The Ml guided approach is advantageous over traditional policies. It learns complex. non linear relationships between different patterns which helps to make optimal decision for caching and helps to achieve better performance.

# ML-Guided Prefetching

For prefetching purpose this research uses machine learning method. It uses machine learning models to predict which data chunks should be prefetched when a cache miss occurs. It is divided into two parts What to prefetch and When to prefetch. In the case of a cache miss, the system relies on trained ML models to predict the chunks, in an episode, that should be pre-fetched based on episode attributes such as access patterns, type of operation, user details and past access history. Offline training of the ML models is performed on features based on the episode accesses to predict the ranges of episode that cannot be identified by simple heuristics. The prefetching is coordinated to the ML admission policy, whereby the prefetched data is admission criteria and offers net service time benefits. ML-guided prefetching using Baleen forecasts the best prefetch range in episodes and uses confidence-based filtering to achieve greater backend load reduction in comparison with traditional methods, which contributes to the overall 12% peak improvement in DT and 17% TCO improvements in the system.

# Episode Based Model

Episode based Model are essential part of this experiment, they treat group of cache residency as a single logical unit in place of single data blocks which is integral part of Baleen's approach for optimizing performance. An episode is a representation of sequence of accesses of data block which forms a logical unit and is essential for cache management decision. These episode based-approach in this experiment enables simulator to make more intelligent caching decisions which take consideration of both performance and flash endurance limitation to make better overall system.

# LRU Eviction Policy

Baseline Eviction policy used in this paper is LRU which stands for Least Recently used. It is simply the eviction policy which removes the item from cache which is not accessed from the longest period of time. The Baseline LRU principle is that when more cache space is needed in cache system, LRU evict the block of data which is least accessed keeping the most recently accessed item. It has several benefit in BCacheSim such as simple and fast implementation, predictable performance and low memory overhead.