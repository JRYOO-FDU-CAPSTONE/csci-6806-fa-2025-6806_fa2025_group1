#!/usr/bin/env python

from argparse import ArgumentParser
from jsonargparse import ArgumentParser, ActionConfigFile, ActionYesNo


from BCacheSim import sim_cache


def get_parser():
    parser = ArgumentParser(description="CacheLib simulator")
    parser.add_argument(
        "--policy",
        "-p",
        type=str,
        choices=["E0_LRU", "E1_DT-SLRU", "E2_EDE"],
        help="Specify the eviction policy to evaluate (choose from 'E0_LRU', 'E1_DT-SLRU', or 'E2_EDE').",
    )

    return parser


def get_parsed_args():
    args = get_parser().parse_args()
    return args


if __name__ == "__main__":
    pass
