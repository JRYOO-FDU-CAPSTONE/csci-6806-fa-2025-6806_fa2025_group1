# Artifact for Baleen (FAST 2024)

[![BCacheSim-RejectX](https://github.com/JRYOO-FDU-CAPSTONE/csci-6806-fa-2025-6806_fa2025_group1/actions/workflows/BCacheSim-RejectX.yml/badge.svg)](https://github.com/JRYOO-FDU-CAPSTONE/csci-6806-fa-2025-6806_fa2025_group1/actions/workflows/BCacheSim-RejectX.yml)
[![BCacheSim-Eviction-Policy](https://github.com/JRYOO-FDU-CAPSTONE/csci-6806-fa-2025-6806_fa2025_group1/actions/workflows/BCacheSim-Eviction-Policy.yml/badge.svg)](https://github.com/JRYOO-FDU-CAPSTONE/csci-6806-fa-2025-6806_fa2025_group1/actions/workflows/BCacheSim-Eviction-Policy.yml)

_Baleen: ML Admission & Prefetching for Flash Caches_

_[Paper (Preprint)](https://wonglkd.fi-de.net/papers/Baleen-FAST24.pdf) | [Code](https://github.com/wonglkd/BCacheSim/) | [Data](https://ftp.pdl.cmu.edu/pub/datasets/Baleen24/) | [Video walkthrough](https://www.tiny.cc/BaleenArtifactYT) | [Reproduce on Chameleon](https://www.chameleoncloud.org/experiment/share/aa6fb454-6452-4fc8-994a-b028bfc3c82d)_

This repository is targeted at those seeking to reproduce the results found in the Baleen paper and contains a frozen copy of the code.
If you are looking to use Baleen, please go to https://github.com/wonglkd/BCacheSim/ for the latest version.

![Artifact Available](https://sysartifacts.github.io/images/usenix_available.svg)
![Artifact Functional](https://sysartifacts.github.io/images/usenix_functional.svg)
![Results Reproduced](https://sysartifacts.github.io/images/usenix_reproduced.svg)

**Scope:** this repository contains Python code to reproduce the **simulator** results in the Baleen paper. The testbed code modified a proprietary internal version of CacheLib and will not be released at this time, pending a rebase on the open-source version of CacheLib. Another key difference is that Meta's exact constants for the disk head time function will not be released, meaning that results will not be exactly the same; instead, we use constants (seek time and bandwidth) measured on the hard disks in our university testbed.

**Nomenclature:**
Some terms were renamed after coding for better clarity in the paper. However, they mean the same thing.

- Service Time (in the code) was renamed to Disk Head Time (in the paper)
- Chunks (in the code) are called segments (in the paper)


## Getting Started

### Requirements

- **Operating System**: Linux (tested on Linux 6.17.5)
- **Python Version**: Python 3.11
- **RAM**: Minimum 8GB (16GB+ recommended for large simulations)
- **Disk Space**: At least 2GB free for output files and cache data
- **Dependencies**: matplotlib, numpy, pandas (install via `pip install -r scripts/reqirements.txt`)

### Setup Instructions (setup/activate Environment)

Clone the repository (if not already done):

```
git clone https://github.com/JRYOO-FDU-CAPSTONE/csci-6806-fa-2025-6806_fa2025_group1.git
cd csci-6806-fa-2025-6806_fa2025_group1
```

Create/Activate Conda Environment (~5 minutes):

```bash
conda env create -f BCacheSim/install/env_cachelib-py-3.11.yaml
conda activate cachelib-py-3.11
```

Install additional dependencies (~2 minutes):

```bash
python3 -m pip install --user -r BCacheSim/install/requirements.txt
python3 -m pip install --user -r scripts/requirements.txt
```

Download trace files (~5 minutes, depending on network speed):

```bash
cd data && bash get-tectonic.sh && cd ..
```

### Reproducing Results (Generate figures)

Create ouput folder:

```bash
mkdir figs
```

#### Minimal Experiments (~2-5 minutes)
```bash
python scripts/run_eviction_experiments_minimal.py --ouput figs/output.pdf
```

#### EDE Figure 1 - Peak DT vs. α_TTI (EWMA) (~30-60 minutes)
Plot showing the relationship between Peak Disk-head Time and the EWMA alpha parameter for Time-To-Idle in the EDE eviction policy.

```bash
python scripts/a5_ede_fig1.py --output figs/a5_ede_fig1.pdf
```

#### EDE Figure 2 - Peak DT vs. PROTECTED Cap (~30-60 minutes)
Plot showing how the Peak Disk-head Time varies with different PROTECTED capacity settings in the EDE eviction policy.

```bash
python scripts/a5_ede_fig2.py --output figs/a5_ede_fig2.pdf
```

#### DT-SLRU Figure 1 - Peak DT vs. DT-per-byte Score (~10-20 minutes)
Plot showing the relationship between Peak Disk-head Time and DT-per-byte scoring threshold in the DT-SLRU eviction policy.

```bash
python scripts/a5_dt_slru_fig1.py --output figs/a5_dt_slru_fig1.pdf
```

#### DT-SLRU Figure 2 - Hit Rate vs. DT-per-byte Score (~10-20 minutes)
Plot showing cache hit rate performance across different DT-per-byte scoring thresholds in the DT-SLRU eviction policy.

```bash
python scripts/a5_dt_slru_fig2.py --output figs/a5_dt_slru_fig2.pdf
```

### Validation Checklist

#### Full Eviction Evaluation

For LRU (baseline) (~2 min):

```bash
python scripts/evaluate_eviction.py --policy E0_LRU
```
Output Format:
```
✔ Loaded config from: runs/example/lru/config.json
✔ Simulation completed in 00:xx
● Peak DT: X.XX ms
```
Expected Peak DT ≈ 1–2 ms


For DT-SLRU (~2 min):

```bash
python scripts/evaluate_eviction.py --policy E1_DT-SLRU
```
Output Format:
```
✔ Loaded config from: runs/example/dt-slru/config.json
✔ Simulation completed in 04:55
● Peak DT: X.XX ms
```
Expected Peak DT ≈ 1–3 ms

For EDE (~10 min):

```bash
python scripts/evaluate_eviction.py --policy E2_EDE
```
Output Format:
```
✔ Loaded config from: runs/example/lru/config.json
✔ Simulation completed in 00:xx
● Peak DT: X.XX ms
```
Expected Peak DT ≈ 1–5 ms


#### Cache Hit Rate Logging (~5 minutes)

```bash
python scripts/log_hit_rate.py --trace data/tectonic/202110/Region4/full_0_0.1.trace
```
Output Format:
```
✔ Loaded config from: runs/example/lru/config.json
✔ Using trace file: data/tectonic/202110/Region4/full_0_0.1.trace
✔ Simulation completed in 00:xx
● Cache Hit Rate: xx.x %
```
Expected Hit Rate: ~75–90%


#### Memory Usage Profiling (~5 minutes)

```bash
python scripts/profile_memory.py
```
Output Format:
```
✔ Loaded config from: runs/example/lru/config.json
✔ Simulation completed in 00:xx
● Peak memory: xxx.x MB
```
Expected Peak Memory: ~1–3 GB


### Limitations

- **Platform Support**: Only tested on Linux systems; may not work on Windows or macOS without modifications
- **Trace Data**: Experiments require Tectonic trace files which are large (~GB range) and may take significant time to download
- **Simulation Time**: Full experiments can take several hours per policy (multiple runs); results are not real-time
- **Memory Constraints**: Large cache simulations may require 16GB+ RAM; running with insufficient memory will cause crashes
- **Single-threaded**: Simulations run sequentially; parallelization requires manual script modification

_Time estimate: 60 mins (20 mins interactive)._

### Installation (Chameleon Trovi)

_Time estimate: 30 minutes (10 mins interactive)._

The recommended way is to use Chameleon Trovi, an academic cloud. Note that you will require an allocation; if you are affiliated with FAST, you can request to be added to the associated project (CHI-231080). To do this (and for any other issues with Chameleon), please contact the helpdesk at help@chameleoncloud.org.

1. Launch [artifact on Trovi](https://www.chameleoncloud.org/experiment/share/aa6fb454-6452-4fc8-994a-b028bfc3c82d)
2. (Optional) Open notebook `chameleon/1-getting-started.ipynb` which will walk you through the Getting Started section of this README. You may run one cell at a time, or click Run -> Run All Cells to execute all commands. If processes get killed, you need a dedicated server.
3. (Recommended) The shared JupyterHub has limited RAM/disk. Run notebook `chameleon/2-start-dedicated-server.ipynb`, which provisions a beefier node (for 7 days) that you can create a SSH tunnel to.

### Installation (local computer)

Alternatively, you may do a manual install. These commands are also available in [getting-started.sh](getting-started.sh) for your convenience.

1. Clone the repository (if not already done)

```
git clone --recurse-submodules https://github.com/wonglkd/Baleen-FAST24.git
cd Baleen-FAST24
```

Note: this repository uses submodules. As a reminder, when you pull, you'll likely want to use `git pull --recurse-submodules`.

2. Install Python dependencies with Conda/Mamba/Micromamba or pip. (We developed with Micromamba 1.4.1.)

```
conda env create -f BCacheSim/install/env_cachelib-py-3.11.yaml
conda activate cachelib-py-3.11
# PyPy is optional (for faster non-ML runs)
# conda env create -f BCacheSim/install/env_cachelib-pypy-3.8.yaml
```

Alternatively, use pip:

```
python3 -m pip install --user -r BCacheSim/install/requirements.txt
```

3. Download trace files (see [here](https://ftp.pdl.cmu.edu/pub/datasets/Baleen24/) for more details on the traces)

```
cd data
bash get-tectonic.sh
```

### Do a simple experiment

_Time estimate: 30 minutes (10 mins interactive)._

1. Manually run the simulator with the baseline RejectX. (4 mins)

```
./BCacheSim/run_py.sh py -B -m BCacheSim.cachesim.simulate_ap --config runs/example/rejectx/config.json
```

2. Manually train Baleen's ML models (25 secs) and run the simulator with Baleen (~30 mins).

```
./BCacheSim/run_py.sh py -B -m BCacheSim.episodic_analysis.train --exp example --policy PolicyUtilityServiceTimeSize2 --region Region1 --sample-ratio 0.1 --sample-start 0 --trace-group 201910 --supplied-ea physical --target-wrs 34 50 100 75 20 10 60 90 30 --target-csizes 366.475 --output-base-dir runs/example/baleen --eviction-age 5892.856 --rl-init-kwargs filter_=prefetch --train-target-wr 35.599 --train-models admit prefetch --train-split-secs-start 0 --train-split-secs-end 86400 --ap-acc-cutoff 15 --ap-feat-subset meta+block+chunk
./BCacheSim/run_py.sh py -B -m BCacheSim.cachesim.simulate_ap --config runs/example/baleen/prefetch_ml-on-partial-hit/config.json
```

3. Scheme E0 - Baseline: admission policy `acceptall` and eviction policy `LRU`, prefetching disabled. (~2 mins)
```
./BCacheSim/run_py.sh py -B -m BCacheSim.cachesim.simulate_ap --config runs/example/lru/config.json
```

4. Scheme E1 - DT-SLRU (Segmented LRU with DT-aware promotion): admission policy `acceptall` and eviction polilcy `DT-SLRU`, prefetching disabled. (~2 mins)
```
./BCacheSim/run_py.sh py -B -m BCacheSim.cachesim.simulate_ap --config runs/example/dt-slru/config.json
```

Run with DT-per-byte (𝜏_DT) set to 0.007:
```
./BCacheSim/run_py.sh py -B -m BCacheSim.cachesim.simulate_ap --config runs/example/dt-slru/config.json --dt-per-byte-score 0.007 --ignore-existing
```

5. Scheme E2 - EDE (Episode-Deadline Eviction): admission policy acceptall and eviction polilcy EDE, prefetching disabled. (~9 mins)
```
./BCacheSim/run_py.sh py -B -m BCacheSim.cachesim.simulate_ap --config runs/example/ede/config.json
```

Generate perf stats for EDE with protected cap factor from 0.0 ~ 0.9, run: (~90 mins)
```
for i in `seq 0 9`;
do
  ./BCacheSim/run_py.sh py -B -m BCacheSim.cachesim.simulate_ap --config runs/example/ede/config.json --ignore-existing --ede-protected-cap 0.${i};
done
```

6. Use [notebooks/example/example.ipynb](notebooks/example/example.ipynb) to view and plot results.

### Do DT-SLRU related experiment

Generate perf stats for DT-SLRU with `dt-per-byte` 0.0002, 0.00265, 0.0051, 0.00755, 0.01 with even spaced: +0.00245

```
for i in 0.0002 0.00265 0.0051 0.00755 0.01;
do
  ./BCacheSim/run_py.sh py -B -m BCacheSim.cachesim.simulate_ap --config runs/example/dt-slru/config.json --dt-per-byte-score $i --ignore-existing;
done
```

Generate perf stats for DT-SLRU with `dt-per-byte` 0.0002, 0.00053, 0.00141, 0.00376, 0.01 with logarithmically spaced: -3.699 to -2, +0.4247 (-3.2743, -2.8496, -2.4249)

```
for i in 0.0002 0.00053 0.00141 0.00376 0.01;
do
  ./BCacheSim/run_py.sh py -B -m BCacheSim.cachesim.simulate_ap --config runs/example/dt-slru/config.json --dt-per-byte-score $i --ignore-existing;
done
```

### Do EDE related experiment

Generate perf stats for EDE with `ede-protected-cap` from 0.1 to 0.9:

```
for i in `seq 1 9`; do ./BCacheSim/run_py.sh py -B -m BCacheSim.cachesim.simulate_ap --config runs/example/ede/config.json --ignore-existing --ede-protected-cap 0.${i}; done
```

Generate perf stats for EDE with `ede-alpha-tti` from 0.1 to 0.9:

```
for i in `seq 1 9`; do ./BCacheSim/run_py.sh py -B -m BCacheSim.cachesim.simulate_ap --config runs/example/ede/config.json --ignore-existing --ede-alpha-tti 0.${i}; done
```

Use [notebooks/example/A5-Ablation.ipynb](notebooks/example/A5-Ablation.ipynb) to view and plot results.

## Detailed Instructions

This section assumes you have completed the 'Getting Started' section and have
installed the code and downloaded the traces.

As it requires too much computation time to rerun every single experiment,
we suggest the following steps to maximize the use of reviewers' time in evaluating
our paper. We supply our traces, code, and the intermediate results from our experimental runs.

**Roadmap for evaluation:**

1. Test out Baleen's ML training & simulator (in Getting Started).
    - What: simulate RejectX baseline, train Baleen models, simulate Baleen
    - Expected results: notebooks/example/example.ipynb
2. Plot graphs using our intermediate results.
    - Example: notebooks/paper-figs/fig-01bc,17-202309.ipynb
3. Select additional simulations to run if desired.
    - See notebooks/reproduce/, in particular commands.ipynb and reproduce_commands.sh


## Directory structure

- data: traces that are used as input
- runs: where experiment results are stored
- tmp: temporary directory for ML models, generated episode files
- notebooks: Jupyter notebooks for experiments
- notebooks/figs: Output directory for figures


## Additional notes

624 machine-days were used for the final runs to generate the results used in the paper.
Each simulation of a ML policy takes at least 30 minutes, multiplied by 7 traces and 10 samples each.

## Future research

notebooks/reproduce/exps-cluster-sample.ipynb will be useful to allow you to run experiments efficiently, but with more dependencies required (brooce, redis).

## Troubleshooting

If you face any issues, please try the following things:

1. Making sure you have the latest version of the repository

```
git pull --recurse-submodules
```

2. Making sure you have the latest copy of the data.

```
cd data
bash clean.sh
bash get-tectonic.sh
```

3. If you need to get an allocation on Chameleon or face any difficulties with the platform itself, please contact their [helpdesk](mailto:help@chameleoncloud.org).

## Any questions?

[Please raise a GitHub issue](https://github.com/wonglkd/Baleen-FAST24/issues/new). Support is best effort; you may also email me (contact details at https://wonglkd.fi-de.net).

## Reference

**[Baleen: ML Admission & Prefetching for Flash Caches](https://www.usenix.org/conference/fast24/presentation/wong)**<br>
Daniel Lin-Kit Wong, Hao Wu, Carson Molder, Sathya Gunasekar, Jimmy Lu, Snehal Khandkar, Abhinav Sharma, Daniel S. Berger, Nathan Beckmann, Gregory R. Ganger<br>
USENIX FAST 2024
