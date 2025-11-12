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


def run_simulation_with_alpha(
    alpha_tti, config_path="runs/example/ede/config.json", verbose=False
):
    """
    Run simulation with specified ede-alpha-tti parameter using subprocess
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
    print(f"\033[33m●\033[0m EDE alpha-tti: {alpha_tti}")

    # Build command to run simulation in subprocess
    cmd = [
        sys.executable,
        "-m",
        "BCacheSim.cachesim.simulate_ap",
        "--config",
        config_path,
        "--ede-alpha-tti",
        str(alpha_tti),
    ]

    # Start spinner
    stop_spinner = threading.Event()
    elapsed_time = [0]

    def spinner_wrapper():
        elapsed_time[0] = show_spinner(
            stop_spinner, f"Running EDE simulation (α={alpha_tti})"
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
    parser = ArgumentParser(description="Generate EDE figure")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="e2-fig1-output.png",
        help="Output file path (supported formats: png, pdf, svg, jpg, jpeg)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show simulation output (default: suppress output)",
    )
    args = parser.parse_args()

    # EDE EWMA alpha values
    ede_ewma_alphas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    # Expected result file paths
    ede_ewma_resultfiles = {
        "EDE-ewma0.1": "runs/example/ede/acceptall-1_lru_366.475GB/full_0_0.1_ewma_0.1_cache_perf.txt.lzma",
        "EDE-ewma0.2": "runs/example/ede/acceptall-1_lru_366.475GB/full_0_0.1_ewma_0.2_cache_perf.txt.lzma",
        "EDE-ewma0.3": "runs/example/ede/acceptall-1_lru_366.475GB/full_0_0.1_ewma_0.3_cache_perf.txt.lzma",
        "EDE-ewma0.4": "runs/example/ede/acceptall-1_lru_366.475GB/full_0_0.1_ewma_0.4_cache_perf.txt.lzma",
        "EDE-ewma0.5": "runs/example/ede/acceptall-1_lru_366.475GB/full_0_0.1_ewma_0.5_cache_perf.txt.lzma",
        "EDE-ewma0.6": "runs/example/ede/acceptall-1_lru_366.475GB/full_0_0.1_ewma_0.6_cache_perf.txt.lzma",
        "EDE-ewma0.7": "runs/example/ede/acceptall-1_lru_366.475GB/full_0_0.1_ewma_0.7_cache_perf.txt.lzma",
        "EDE-ewma0.8": "runs/example/ede/acceptall-1_lru_366.475GB/full_0_0.1_ewma_0.8_cache_perf.txt.lzma",
        "EDE-ewma0.9": "runs/example/ede/acceptall-1_lru_366.475GB/full_0_0.1_ewma_0.9_cache_perf.txt.lzma",
    }

    # Map alpha values to result files
    alpha_to_resultfile = {
        0.1: ede_ewma_resultfiles["EDE-ewma0.1"],
        0.2: ede_ewma_resultfiles["EDE-ewma0.2"],
        0.3: ede_ewma_resultfiles["EDE-ewma0.3"],
        0.4: ede_ewma_resultfiles["EDE-ewma0.4"],
        0.5: ede_ewma_resultfiles["EDE-ewma0.5"],
        0.6: ede_ewma_resultfiles["EDE-ewma0.6"],
        0.7: ede_ewma_resultfiles["EDE-ewma0.7"],
        0.8: ede_ewma_resultfiles["EDE-ewma0.8"],
        0.9: ede_ewma_resultfiles["EDE-ewma0.9"],
    }

    # Check which result files exist and run simulations for missing ones
    print("\033[1m=== Checking result files ===\033[0m")
    for alpha_value in ede_ewma_alphas:
        result_file = alpha_to_resultfile[alpha_value]
        if os.path.exists(result_file):
            print(f"\033[32m✔\033[0m Found: {result_file}")
        else:
            print(f"\033[33m✗\033[0m Missing: {result_file}")
            print(
                f"\033[36m→\033[0m Running simulation with ede-alpha-tti={alpha_value}"
            )
            run_simulation_with_alpha(alpha_value, verbose=args.verbose)

    print("\n\033[1m=== Loading results ===\033[0m")

    # Load all results
    ede_ewma_res = {}
    for label, filename in ede_ewma_resultfiles.items():
        if os.path.exists(filename):
            print(f"\033[32m✔\033[0m Loading: {label}")
            full_path = str(PROJECT_ROOT / filename)
            ede_ewma_res[label] = results.get(
                {"Region": "Region1", "Filename": full_path}
            )
        else:
            print(f"\033[31m✗\033[0m Cannot load: {label} (file not found: {filename})")

    # Create dataframe from results
    if ede_ewma_res:
        ede_ewma_rows = []
        for label, resv in ede_ewma_res.items():
            resv.summary["Label"] = label
            ede_ewma_rows.append(resv.summary)
        ede_ewma_df = pd.concat(ede_ewma_rows)

        print(f"\n\033[1m=== Results Summary ===\033[0m")
        print(ede_ewma_df)

        # Create plot
        plt.plot(
            ede_ewma_df["α_TTI"],
            ede_ewma_df["PeakServiceTimeUsed1"],
            marker="x",
            linewidth=3,
            color="tab:green",
            label="EDE",
        )

        plt.xticks(rotation=45)
        plt.title("Peak DT vs. α_TTI (EWMA)")
        plt.xlabel("α_TTI")
        plt.ylabel("Peak DT (ms)")
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
