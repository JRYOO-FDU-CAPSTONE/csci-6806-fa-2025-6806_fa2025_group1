#!/usr/bin/env python

import contextlib
import json
import os
import sys
from pathlib import Path

from jsonargparse import ArgumentParser

# Add project to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from BCacheSim.cachesim import sim_cache, simulate_ap


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

            print(f"Loaded config from: \033[32m{config_path}\033[0m")

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

    with contextlib.redirect_stdout(open(os.devnull, "w")):
        stats = sim_cache.simulate_cache_driver(args)

    # print(stats)

    print(stats["results"]["PeakServiceTimeUsed1"])


if __name__ == "__main__":
    main()
