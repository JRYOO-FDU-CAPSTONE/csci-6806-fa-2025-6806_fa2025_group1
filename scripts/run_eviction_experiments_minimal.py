#!/usr/bin/env python

"""
Minimal script to load and plot eviction experiment results.
"""

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from jsonargparse import ArgumentParser

# Add project to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import results module
from BCacheSim.episodic_analysis.exps import results

# Parse command line arguments
parser = ArgumentParser(description="Load and plot eviction experiment results")
parser.add_argument(
    "-o",
    "--output",
    type=str,
    default="output.png",
    help="Output file path (supported formats: png, pdf, svg, jpg, jpeg)",
)
args = parser.parse_args()

# Define result files
resultfiles = {
    "LRU": "runs/example/lru/acceptall-1_lru_366.475GB/full_0_0.1_cache_perf.txt.lzma",
    "DT-SLRU": "runs/example/dt-slru/acceptall-1_lru_366.475GB/full_0_0.1_cache_perf.txt.lzma",
    "EDE": "runs/example/ede/acceptall-1_lru_366.475GB/full_0_0.1_cache_perf.txt.lzma",
}

# Load results
res = {}
for label, filename in resultfiles.items():
    print(f"\n{label}: {filename}")
    # Use absolute path based on PROJECT_ROOT instead of relative path
    full_path = str(PROJECT_ROOT / filename)
    print(f"  Full path: {full_path}")
    print(f"  Exists: {os.path.exists(full_path)}")
    res[label] = results.get({"Region": "Region1", "Filename": full_path})
    print(f"  Has summary: {hasattr(res[label], 'summary')}")
    if hasattr(res[label], 'summary'):
        print(f"  Summary is None: {res[label].summary is None}")

# Debug output
print("\n" + "="*50)
print(res["DT-SLRU"])
print(res["DT-SLRU"].summary)
print("="*50 + "\n")

# Plot results
ax = plt.gca()
for label, resv in res.items():
    if hasattr(resv, 'progress') and resv.progress is not None:
        d_ = res[label].progress["GET+PUT"][600]
        d_["Days"] = d_["Elapsed Trace Time"] / 3600 / 24
        d_.plot(x="Days", y="Util", ax=ax, label=label)
    else:
        print(f"Warning: No progress data for {label}")

plt.legend()
plt.xlabel("Days")
plt.ylabel("Utilization")
plt.title("Backend Utilization Over Time")
plt.grid(True, alpha=0.3)

# Determine format from file extension
output_path = args.output
file_ext = Path(output_path).suffix.lower()
format_map = {
    ".png": "png",
    ".pdf": "pdf",
    ".svg": "svg",
    ".jpg": "jpg",
    ".jpeg": "jpg",
}
output_format = format_map.get(file_ext, "png")

plt.savefig(output_path, format=output_format, dpi=300, bbox_inches="tight")
print(f"\nPlot saved to {output_path} (format: {output_format})")
plt.show()
