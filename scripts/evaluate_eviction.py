#!/usr/bin/env python

import contextlib
import json
import os
import sys
import threading
import itertools
import time
from pathlib import Path

from jsonargparse import ArgumentParser

# Add project to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from BCacheSim.cachesim import sim_cache, simulate_ap


def show_spinner(stop_event, message="Running simulation"):
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    # Write directly to terminal file descriptor
    tty = open('/dev/tty', 'w')
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
        tty.write(f'\r\033[34m{next(spinner)}\033[0m {message} ... \033[36m[{time_str}]\033[0m')
        tty.flush()
        time.sleep(0.1)

    # Clear line
    elapsed = time.time() - start_time
    tty.write('\r\033[K')
    tty.flush()
    tty.close()

    return elapsed


def get_parser():
    parser = ArgumentParser(description="Evaluate Eviction")
    parser.add_argument(
        "--policy",
        "-p",
        required=True,
        type=str,
        choices=["E0_LRU", "E1_DT-SLRU", "E2_EDE"],
        help="Specify the eviction policy to evaluate ('E0_LRU', 'E1_DT-SLRU', or 'E2_EDE')",
    )

    return parser


def get_parsed_args():
    args = get_parser().parse_args()
    return args


def load_config_for_policy(args):
    """
    Load and validate config file for the selected policy
    """
    config_path = None

    if args.policy == "E0_LRU":
        config_path = "runs/example/lru/config.json"
    elif args.policy == "E1_DT-SLRU":
        config_path = "runs/example/dt-slru/config.json"
    elif args.policy == "E2_EDE":
        config_path = "runs/example/ede/config.json"

    if config_path:
        if not os.path.exists(config_path):
            print(
                f"Error: Config file '{config_path}' not found for {args.policy} policy.",
                file=sys.stderr,
            )
            print(
                f"Please ensure the config file exists at: {os.path.abspath(config_path)}",
                file=sys.stderr,
            )
            sys.exit(1)

        # Load the config file
        try:
            # with open(config_path, "r") as f:
            #     config_data = json.load(f)

            parser = simulate_ap.get_parser()
            args = parser.parse_args(["--config", config_path])

            print(f"\033[32m✔\033[0m Loaded config from: \033[32m{config_path}\033[0m")

            # Merge config data into args
            # for key, value in config_data.items():
            #     setattr(args, key, value)

            # return args

        except json.JSONDecodeError as e:
            print(
                f"Error: Failed to parse config file '{config_path}': {e}",
                file=sys.stderr,
            )
            sys.exit(1)
        except Exception as e:
            print(
                f"Error: Failed to load config file '{config_path}': {e}",
                file=sys.stderr,
            )
            sys.exit(1)

    return args


def main():
    args = get_parsed_args()
    policy = args.policy

    args = load_config_for_policy(args)
    assert args.trace or args.tracefile

    if args.trace:
        args.tracefile = args.trace
    if args.config:
        args.config = [str(x) for x in args.config]
    assert not (args.fifo and args.lirs), "Cannot run with both fifo and lirs"

    args.ignore_existing = True
    # args.cache_elems = None
    # args.offline_ap_decisions = None
    # args.learned_ap_granularity = None
    # args.early_evict = None
    # args.prefetch = None
    # args.cachelib_trace = None
    # args.limit = None
    # args.ap_chunk_threshold = None

    stats = {"options": None, "results": None}

    # Start spinner
    stop_spinner = threading.Event()
    elapsed_time = [0]

    def spinner_wrapper():
        elapsed_time[0] = show_spinner(stop_spinner, f"Running eviction simulation for {policy}")

    spinner_thread = threading.Thread(target=spinner_wrapper)
    spinner_thread.start()

    # Redirect stdout and stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

    try:
        stats = sim_cache.simulate_cache_driver(args)
    finally:
        # Restore
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = old_stdout
        sys.stderr = old_stderr

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

    print(f"\033[32m●\033[0m Peak DT ", {stats["results"]["PeakServiceTimeUsed1"]})


if __name__ == "__main__":
    main()
