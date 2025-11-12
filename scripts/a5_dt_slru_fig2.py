#!/usr/bin/env python

import contextlib
import itertools
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from jsonargparse import ArgumentParser

# Add project to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import results module
from BCacheSim.episodic_analysis.exps import results


def show_spinner(stop_event, message="Running simulation"):
    spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    # Write directly to terminal file descriptor
    tty = open("/dev/tty", "w")
    start_time = time.time()

    while not stop_event.is_set():
        elapsed = time.time() - start_time
        hours, remainder = divmod(int(elapsed), 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = f"{minutes:02d}:{seconds:02d}"

        # Blue spinner (\033[34m) and cyan time
        tty.write(
            f"\r\033[34m{next(spinner)}\033[0m {message} ... \033[36m[{time_str}]\033[0m"
        )
        tty.flush()
        time.sleep(0.1)

    # Clear line
    elapsed = time.time() - start_time
    tty.write("\r\033[K")
    tty.flush()
    tty.close()

    return elapsed


def run_simulation_with_dt(
    dt_per_byte_score, config_path="runs/example/dt-slru/config.json", verbose=False
):
    """
    Run simulation with specified dt-per-byte-score parameter using subprocess
    """
    if not os.path.exists(config_path):
        print(
            f"Error: Config file '{config_path}' not found.",
            file=sys.stderr,
        )
        print(
            f"Please ensure the config file exists at: {os.path.abspath(config_path)}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"\033[32m✔\033[0m Using config: \033[32m{config_path}\033[0m")
    print(f"\033[33m●\033[0m DT-per-byte-score: {dt_per_byte_score}")

    # Build command to run simulation in subprocess
    cmd = [
        sys.executable,
        "-m",
        "BCacheSim.cachesim.simulate_ap",
        "--config",
        config_path,
        "--dt-per-byte-score",
        str(dt_per_byte_score),
    ]

    # Start spinner
    stop_spinner = threading.Event()
    elapsed_time = [0]

    def spinner_wrapper():
        elapsed_time[0] = show_spinner(
            stop_spinner, f"Running DT-SLRU simulation (τ={dt_per_byte_score})"
        )

    spinner_thread = threading.Thread(target=spinner_wrapper)
    spinner_thread.start()

    try:
        # Run simulation in subprocess
        if verbose:
            result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
        else:
            result = subprocess.run(
                cmd,
                cwd=str(PROJECT_ROOT),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        if result.returncode != 0:
            print(
                f"\n\033[31m✗ Simulation failed with exit code {result.returncode}\033[0m"
            )
            sys.exit(1)

    finally:
        # Stop spinner
        stop_spinner.set()
        spinner_thread.join()

    hours, remainder = divmod(int(elapsed_time[0]), 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        time_str = f"{minutes:02d}:{seconds:02d}"

    print(f"\033[32m✔ Simulation completed\033[0m in \033[36m{time_str}\033[0m")


def main():
    # Parse command line arguments
    parser = ArgumentParser(description="Generate DT-SLRU figure")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="e1-fig2-output.png",
        help="Output file path (supported formats: png, pdf, svg, jpg, jpeg)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show simulation output (default: suppress output)",
    )
    args = parser.parse_args()

    # DT-SLRU tau values (dt-per-byte-score)
    dt_slru_tau_dts = [0.0002, 0.00053, 0.00141, 0.00376, 0.01]

    # Expected result file paths
    dt_slru2_resultfiles = {
        "DT-SLRU_0.0002": "runs/example/dt-slru/acceptall-1_lru_366.475GB/full_0_0.1_0.0002_cache_perf.txt.lzma",
        "DT-SLRU_0.00053": "runs/example/dt-slru/acceptall-1_lru_366.475GB/full_0_0.1_0.00053_cache_perf.txt.lzma",
        "DT-SLRU_0.00141": "runs/example/dt-slru/acceptall-1_lru_366.475GB/full_0_0.1_0.00141_cache_perf.txt.lzma",
        "DT-SLRU_0.00376": "runs/example/dt-slru/acceptall-1_lru_366.475GB/full_0_0.1_0.00376_cache_perf.txt.lzma",
        "DT-SLRU_0.010": "runs/example/dt-slru/acceptall-1_lru_366.475GB/full_0_0.1_0.01_cache_perf.txt.lzma",
    }

    # Map dt values to result files
    dt_to_resultfile = {
        0.0002: dt_slru2_resultfiles["DT-SLRU_0.0002"],
        0.00053: dt_slru2_resultfiles["DT-SLRU_0.00053"],
        0.00141: dt_slru2_resultfiles["DT-SLRU_0.00141"],
        0.00376: dt_slru2_resultfiles["DT-SLRU_0.00376"],
        0.01: dt_slru2_resultfiles["DT-SLRU_0.010"],
    }

    # Check which result files exist and run simulations for missing ones
    print("\033[1m=== Checking result files ===\033[0m")
    for dt_value in dt_slru_tau_dts:
        result_file = dt_to_resultfile[dt_value]
        if os.path.exists(result_file):
            print(f"\033[32m✔\033[0m Found: {result_file}")
        else:
            print(f"\033[33m✗\033[0m Missing: {result_file}")
            print(
                f"\033[36m→\033[0m Running simulation with dt-per-byte-score={dt_value}"
            )
            run_simulation_with_dt(dt_value, verbose=args.verbose)

    print("\n\033[1m=== Loading results ===\033[0m")

    # Load all results
    dt_slru2_res = {}
    for label, filename in dt_slru2_resultfiles.items():
        if os.path.exists(filename):
            print(f"\033[32m✔\033[0m Loading: {label}")

            full_path = str(PROJECT_ROOT / filename)
            dt_slru2_res[label] = results.get(
                {"Region": "Region1", "Filename": full_path}
            )
        else:
            print(f"\033[31m✗\033[0m Cannot load: {label} (file not found: {filename})")

    # Create dataframe from results
    if dt_slru2_res:
        dt_slru2_rows = []
        for label, resv in dt_slru2_res.items():
            resv.summary["Label"] = label
            dt_slru2_rows.append(resv.summary)
        dt_slru2_df = pd.concat(dt_slru2_rows)

        print(f"\n\033[1m=== Results Summary ===\033[0m")
        print(dt_slru2_df)

        plt.plot(
            dt_slru2_df["DT-per-byte Score"],
            dt_slru2_df["Hit Rate (Hz)"],
            marker="x",
            linewidth=3,
            color="tab:green",
            label="DT-SLRU",
        )

        # plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))
        plt.xticks(rotation=45)
        plt.title("Hit Rate (Hz) vs. DT-per-byte Score")
        plt.xlabel("DT-per-byte Score")
        plt.ylabel("Hit Rate (hz)")
        plt.grid(True)
        plt.legend(title="Eviction Policy")

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

        # Save plot
        print(
            f"\n\033[32m✔\033[0m Saving plot to {output_path} (format: {output_format})"
        )
        plt.savefig(output_path, format=output_format, dpi=300, bbox_inches="tight")
        plt.show()
    else:
        print("\n\033[31mError: No results available to plot\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main()
