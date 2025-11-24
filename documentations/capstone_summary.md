# Capstone Project Summary

## 1. Overview

This document summarizes the CSCI6806 Capstone Project (Fall 2025), conducted at Fairleigh Dickinson University (Vancouver Campus) by Anna Gorislavets, Bikash Shyangtang, Hao Chen, Maoting Li, and Salinrat Thanathapsakun.

The project explores the evaluation and reproduction of the Baleen flash caching system proposed in "Baleen: ML Admission & Prefetching for Flash Caches" (USENIX FAST'24) - a system that optimizes flash cache usage in large-scale data centers by reducing peak backend load (Disk-head Time or DT) through ML–guided admission and prefetching.

The document serves as an overview of the group's research and progress throughout the project.  
It connects all submitted assignments (A1-A6) into a cohesive narrative that reflects both the theoretical foundation and the practical methodology of our work.

---

## 2. Motivation

Modern data centers rely on hybrid storage architectures, where HDDs provide capacity and SSDs absorb peak I/O load.  
However, SSDs have limited write endurance, so it is inefficient to cache every I/O miss.  
This constraint necessitates intelligent admission and eviction policies that decide which data blocks should be written into flash and which should be discarded to maximize performance and minimize wear.

Traditional policies such as RejectX and DT-SLRU address these trade-offs heuristically but fail to consider long-term flash endurance and backend load together.  
Baleen proposes an ML-based approach that redefines caching optimization using an episode-based model, focusing on DT - a more accurate measure of backend utilization than hit rate or byte miss rate.

---

## 3. Background (A1)

Our first stage focused on understanding flash cache fundamentals and the DT metric, which is the time a disk head spends serving backend requests.  
We studied how Peak DT determines storage capacity requirements, and why minimizing Peak DT reduces both latency and infrastructure cost.

We also explored the episode model, which treats each cache residency as a single unit, reflecting the real cost of a flash admission more precisely than hit-rate–based metrics.  
This model forms the foundation for Baleen's offline Optimal Admission Policy (OPT), used to train ML models that imitate OPT decisions while adhering to flash write-rate limits.

---

## 4. Related Work (A2)

In the second stage, we surveyed a decade of research on hybrid storage and flash caching.  
We analyzed works that explored:
- Hybrid HDD–SSD architectures and endurance-cost trade-offs;
- Selective and probabilistic admission policies such as Flashield and OP-FCL;
- ML and reinforcement learning approaches, including Learning Relaxed Bélády (LRB) and RL-Bélády (RLB).

These studies gradually evolved toward Baleen's holistic design, which coordinates admission, prefetching, and endurance modeling together.  
Earlier systems optimized hit rates or byte misses, but Baleen's focus on DT and Total Cost of Ownership (TCO) provides a more robust, system-level optimization framework.

---

## 5. Methodology (A3)

The third stage focused on reproducing and analyzing the Baleen-FAST24 artifact, the open-source simulator that accompanied the FAST'24 paper.  
The artifact includes the BCacheSim simulator, trace datasets, ML model scripts, and notebooks for experiment replication.

Our group reviewed:
- The repository's structure and experiment configuration;
- Definitions of key metrics: DT, Peak DT, Flash Write Rate, TCO, and Cache Hit Rate;
- Planned comparisons between baseline heuristics (RejectX, CoinFlip) and Baleen's ML-guided policies;
- Training parameters, workload splits, and evaluation methodology aligned with the paper.

This phase established the foundation for our subsequent evaluation and reporting.

---

## 6. Evaluation (A4)

The fourth stage focused on interpreting experimental results from the Baleen simulator.  
We analyzed Peak DT, Median DT, Cache Hit Rate, and Cache Size Sensitivity across various eviction schemes, including Baleen, RejectX, EDE, Baseline, and DT-SLRU.

Key findings:
- Baleen consistently outperforms other policies, reducing Peak DT by approximately 12% and TCO by 17% relative to the best baseline;  
- Median DT remained stable, confirming that Baleen reduces tail latency without compromising average performance;
- RejectX improves efficiency modestly but lacks Baleen's adaptive coordination;
- DT-SLRU and EDE exhibit higher service times even under light loads, emphasizing the benefit of ML-guided coordination between admission and prefetching.

These observations validate Baleen's claim: coordinated ML-driven caching policies can reduce backend load while maintaining flash endurance.

---

## 7. Ablation Study (A5)

The fifth stage focused on an ablation study of Baleen's baseline policies (DT-SLRU and EDE) to evaluate how internal parameters affect performance.  
All experiments were run using the provided Tectonic traces and the Baleen-FAST24 simulation setup.

We examined the sensitivity of:
- 𝜏DT - DT-per-byte admission threshold (DT-SLRU);
- PROTECTED cap - size of the protected region (EDE);
- 𝛼tti - smoothing factor for time-to-idle (EDE).

Across all experiments, parameter changes produced less than 1% variation in Peak DT, confirming that Baleen and its baselines are stable and robust under moderate configuration changes.

Key observations:
- Very small 𝜏DT values over-admit blocks and increase Peak DT, very large values underutilize flash;
- PROTECTED cap had minimal impact, suggesting EDE's decisions rely primarily on deadlines;
- 𝛼tti values around 0.5-0.7 yielded the best balance between responsiveness and stability.

These results support the paper's claim that Baleen's performance does not depend on fine-tuned thresholds and generalizes well across workloads.

---

## 8. Abstract, Introduction, and Conclusion (A6)

The sixth stage focused on writing the Abstract, Introduction, and Conclusion for the capstone report.
This assignment consolidated our understanding of Baleen and required presenting the problem, motivation, prior solutions, Baleen's design, and the project's contributions in an academic form.

Work completed during this assignment:
- The Abstract summarized the goal of evaluating Baleen's key parameters (𝜏DT, PROTECTED cap, 𝛼tti) and highlighted the main quantitative findings from A4-A5;
- The Introduction explained the limitations of traditional caching policies, the motivation for using DT as a backend-load metric, and how Baleen's episode model and ML-based approach address these issues;
- The Conclusion summarized the experimental results, emphasizing Baleen's robustness, low parameter sensitivity, and predictable performance.

This stage translated the technical findings from A1-A5 into polished academic writing aligned with FAST'24 style expectations.

---

## 9. Final Report (A9)

The last stage focused on assembling the complete final report, combining all major sections: Abstract, Introduction, Background, Related Work, Methodology, Evaluation, Discussion, Ablation Study, Conclusion, Member Contributions, and References.

Work completed during this stage:
- Integrated all prior assignments (A1-A6) into a single coherent document;
- Rewrote transitional parts to ensure flow, removed redundancy, and aligned terminology across sections;
- Added the Discussion, highlighting the importance of Peak DT, the significance of Baleen's robustness, and future extensions such as broader workloads, admission-prefetch interactions, and real-system validation;
- Organized the Ablation Study as a standalone section in the full paper, with clearer motivation and analytical framing;
- Ensured ACM-style formatting, citation consistency, and figure alignment;
- Finalized Member Contributions and References per course requirements.

A9 marks the completion of the project by unifying all technical and analytical work into the final, publication-ready report.

---

## 10. Project Timeline

| Assignment | Focus | Summary of Work |
|-----------|--------|------------------|
| A1 | Background | Introduced flash caching basics, DT metric, and motivation for optimizing backend load |
| A2 | Related Work | Surveyed prior research in hybrid storage, selective admission, and ML-driven caching |
| A3 | Methodology | Analyzed the Baleen-FAST24 artifact, experiment structure, and key performance metrics |
| A4 | Evaluation | Interpreted Baleen vs. baseline results (Peak DT, Median DT, hit rate, flash write rate) |
| A5 | Ablation Study | Evaluated parameter sensitivity (𝜏DT, PROTECTED cap, 𝛼tti) |
| A6 | Abstract, Introduction, and Conclusion | Summarized our work in Abstract, Introduction, and Conclusion sections for the final report |
| A9 | Final Report | Combined all sections into a unified report, added Discussion, refined formatting |
