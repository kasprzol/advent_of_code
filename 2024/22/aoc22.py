import argparse
import collections
import concurrent.futures
import enum
import functools
import gc
import heapq
import io
import itertools
import operator
import re
from collections import defaultdict, deque
from dataclasses import dataclass, field
from fractions import Fraction
from io import TextIOWrapper
from pathlib import Path
from typing import Iterable, NamedTuple

from rich import print
from rich.pretty import pprint
from tqdm.rich import tqdm, trange

VERBOSE = False


def load_input(indata: TextIOWrapper):
    secrets = []
    for row_idx, line in enumerate(indata):
        line = line.strip().split("#")[0]
        if not line:
            continue
        secrets.append(int(line))
    return secrets


def generate_new_secret(old: int) -> int:
    def mix(num):
        return num ^ old

    def prune(num):
        return num % 16777216  # 2 ** 24

    new = prune(mix(old * 64))
    old = new
    new = prune(mix(new // 32))
    old = new
    new = prune(mix(new * 2048))
    return new


def part1(input_file: TextIOWrapper):
    secret_numbers = load_input(input_file)
    secret_number_iterations = 2000
    result = 0
    for buyer in secret_numbers:
        initial = buyer
        for i in range(secret_number_iterations):
            buyer = generate_new_secret(buyer)
        if VERBOSE:
            print(f"{initial} -> {buyer}")
        result += buyer
    print(f"Part 1: {result:,}")


def part2(input_file: TextIOWrapper):
    print(f"Part 2: {0:,}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", type=int, choices=[1, 2])
    parser.add_argument("input", type=argparse.FileType("r"), default="test_input.txt")
    parser.add_argument("-v", "--verbose", action="store_true")
    arguments = parser.parse_args()
    global VERBOSE
    VERBOSE = arguments.verbose
    if arguments.part == 1:
        part1(arguments.input)
    elif arguments.part == 2:
        part2(arguments.input)


if __name__ == "__main__":
    main()
