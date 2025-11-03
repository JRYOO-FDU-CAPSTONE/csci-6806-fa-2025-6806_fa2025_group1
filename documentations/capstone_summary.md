# Capstone Project Summary

## 1. Overview

This document summarizes the **CSCI6806 Capstone Project (Fall 2025)**, conducted at *Fairleigh Dickinson University (Vancouver Campus)* by **Anna Gorislavets, Bikash Shyangtang, Hao Chen, Maoting Li, and Salinrat Thanathapsakun**.

The project explores the **evaluation and reproduction of the Baleen flash caching system** proposed in *“Baleen: ML Admission & Prefetching for Flash Caches” (USENIX FAST’24)* - a system that optimizes flash cache usage in large-scale data centers by **reducing peak backend load (Disk-head Time)** through *ML–guided admission and prefetching*.

The document serves as an overview of the group’s research and progress throughout the project.  
It connects all submitted assignments (A1-A5) into a cohesive narrative that reflects both the theoretical foundation and the practical methodology of our work.

---

## 2. Motivation

Modern data centers rely on hybrid storage architectures, where **HDDs provide capacity** and **SSDs absorb peak I/O load**.  
However, SSDs have **limited write endurance**, so it is inefficient to cache every I/O miss.  
This constraint necessitates intelligent admission and eviction policies that decide *which data blocks should be written into flash* and *which should be discarded* to maximize performance and minimize wear.

Traditional policies such as RejectX and DT-SLRU address these trade-offs heuristically but fail to consider long-term flash endurance and backend load together.  
Baleen proposes an ML-based approach that redefines caching optimization using an **episode-based model** and focuses on **Disk-head Time (DT)** - a more accurate measure of backend utilization than hit rate or byte miss rate.

---
