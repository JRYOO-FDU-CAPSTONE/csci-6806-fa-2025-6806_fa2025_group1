# BCacheSim

It is a Cache Simulator for Flash Caching in Bulk Storage. It is a specialized cache simulator designed and developed as a part of Baleen research project. It mainly focuses on optimizing flash cache performance in large scale data centers.

The simulator specifically addresses the limited write endurance of SSDs by implementing some intelligent admission and eviction policies to make the best decisions regarding which blocks of data should be written to the flash and which blocks can be discarded, based on Disk-head Time (DT) as a more accurate metric on backend utilization than the traditional hit rate metrics. The system uses a system of machine learning-based admission and prefetching policies such as the advanced Baleen algorithm, as well as traditional methods such as RejectX and CoinFlip. BCacheSim is used to process the traces of real-world applications from large-scale storage systems such as Meta's Tectonic filesystem, apply different caching policies, and generate comprehensive performance metrics such as service time utilization, service time peak analysis, IOPs saved ratios, cache hit rates, write rates, and prefetch effectiveness.

It has several key features that make it unique from the traditional cache simulators and allow for sophisticated analysis of flash caching systems. The Flash cache specially focuses on problem of hybrid architecture where SSD's are used for caching purpose, implementing Ml guided policies to optimize performance minimizing the limitation of write endurance. It uses Disk-Head Time as main parameter which is an accurate measure in terms of disk utilization which also help to predict better performance.

# Disk-Head Time

# ML-Guided Policies

# Eviction Policies
