

This document intends to be a documentation we did for the ede eviction policy.

# Overview of EDE 


The Episode-Deadline Eviction (EDE) policy is a sophisticated cache eviction strategy designed specifically for flash-based storage systems.

EDE predicts when cached items will become idle and evicts items that are closest to their predicted expiration time,

while protecting high-value items based on their service-time-per-byte (DT-per-byte) characteristics.


