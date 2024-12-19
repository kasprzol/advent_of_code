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
from tqdm.rich import tqdm, trange

VERBOSE = False

patterns = []


def load_input(indata: TextIOWrapper):
    designs = []
    patterns.extend(indata.readline().strip().split(", "))
    for row_idx, line in enumerate(indata):
        line = line.split("#")[0].strip()
        if not line:
            continue
        designs.append(line)
    return patterns, designs


@functools.cache
def make_design_from_patterns(design):
    candidates = []
    if design == "":
        # we successfully created the required design
        return True, []
    for pattern in patterns:
        if design.startswith(pattern):
            candidates.append(pattern)
    for pattern in candidates:
        if make_design_from_patterns(design.removeprefix(pattern)):
            return True
    return False


def part1(input_file: TextIOWrapper):
    patterns, designs = load_input(input_file)

    possible_designs = 0
    for design in tqdm(designs, desc="designs"):
        if make_design_from_patterns(design):
            possible_designs += 1

    print(f"Part 1: {possible_designs:,}")


@functools.cache
def make_design_from_patterns2(design):
    candidates = []
    if design == "":
        # we successfully created the required design
        return 1
    for pattern in patterns:
        if design.startswith(pattern):
            candidates.append(pattern)
    number_of_combinations = 0
    for pattern in candidates:
        res = make_design_from_patterns2(design.removeprefix(pattern))
        if res:
            number_of_combinations += res
    return number_of_combinations


def part2(input_file: TextIOWrapper):
    patterns, designs = load_input(input_file)

    possible_designs = 0
    for design in tqdm(designs, desc="designs"):
        if number_of_combinations := make_design_from_patterns2(design):
            if VERBOSE:
                print(f"Number of combinations for design {design}: {number_of_combinations}")
            possible_designs += number_of_combinations

    print(f"Part 2: {possible_designs:,}")


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
