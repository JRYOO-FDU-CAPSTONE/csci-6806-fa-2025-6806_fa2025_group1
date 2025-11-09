# BCacheSim

It is a Cache Simulator for Flash Caching in Bulk Storage. It is a specialized cache simulator designed and developed as a part of Baleen research project. It mainly focuses on optimizing flash cache performance in large scale data centers.

The simulator specifically addresses the limited write endurance of SSDs by implementing some intelligent admission and eviction policies to make the best decisions regarding which blocks of data should be written to the flash and which blocks can be discarded, based on Disk-head Time (DT) as a more accurate metric on backend utilization than the traditional hit rate metrics. The system uses a system of machine learning-based admission and prefetching policies such as the advanced Baleen algorithm, as well as traditional methods such as RejectX and CoinFlip. BCacheSim is used to process the traces of real-world applications from large-scale storage systems such as Meta's Tectonic filesystem, apply different caching policies, and generate comprehensive performance metrics such as service time utilization, service time peak analysis, IOPs saved ratios, cache hit rates, write rates, and prefetch effectiveness.

It has several key features that make it unique from the traditional cache simulators and allow for sophisticated analysis of flash caching systems. The Flash cache specially focuses on problem of hybrid architecture where SSD's are used for caching purpose, implementing Ml guided policies to optimize performance minimizing the limitation of write endurance. It uses Disk-Head Time as main parameter which is an accurate measure in terms of disk utilization which also help to predict better performance.

# Disk-Head Time

Disk-Head time is defined as time a disk spend on fulfilling the request on backend. It is one of the accurate metric for the storage system ultization than the traditional metric of hit rate and miss rate. The metric like hit rate and miss rate uses the count of hit and miss whenever there is a request for the service. Unlike this  Disk Head time calculates the total time spent on disk seek time, rotational delays and data transfer when request are served from the backend storage not from cache. 

In this BcacheSim simulator, DT is used as main parameter which is taken in account for all admission and eviction policies which aims for the minimum Peak DT instead of only maximizing hit rates. Simulator is used to observe the peak DT over different parameters so it can be analyzed properly and which can help in the study of different cache policies and their impact.

# ML-Guided Policies

Ml-Guided pilicies is an approach made for efficient cache management using machine learning to make proper addmission and prefeteching decision to reduce Peak DT. It is very different from tradition heuristic based policies which is based on fixed threshold or rules, these Ml-guided policies are trained on episode based features to predict whether to admit the particular episode or exclude the episode so it can benefit the flash write cost. The ML-guided training is based on optimal addmission Policy (OPT) which can make addmission decisions and train ML models to utilize that optimal decision maintaing flash write constraints. 

For this ML approach episode based model is used which treats each cache residency as a single logical unit instead of whole individual block of data. It is very useful for Ml model to learn the patterns about access sequence and make decision for optimizing the episode lifecycle. Being based on these ML model is implemented by simulator which predict which block are likely to be accessed in future which enable proactive admission of data before it is requested.

The Ml guided approach is advantageous over traditional policies. It learns complex. non linear relationships between different patterns which helps to make optimal decision for caching and helps to achieve better performance.
