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
import typing
from collections import defaultdict, deque
from dataclasses import dataclass, field
from fractions import Fraction
from io import TextIOWrapper
from pathlib import Path
from typing import Iterable, NamedTuple, TypedDict

from rich import print
from rich.pretty import pprint
from tqdm import tqdm, trange

VERBOSE = False


def load_input(indata: TextIOWrapper) -> tuple[list[list[int]], list[list[int]]]:
    first_line_of_schematics = True
    lock_or_key = None
    schematic = []
    locks = []
    keys = []

    def transpose(array2d: list[list[typing.Any]]) -> list[list[typing.Any]]:
        ret = list(zip(*array2d))
        return ret

    for row_idx, line in enumerate(indata):
        line = line.strip()
        if line == "":
            heights = transpose(schematic)
            heights = [i.count("#") - 1 for i in heights]
            if lock_or_key == "key":
                keys.append(heights)
            else:
                locks.append(heights)
            schematic = []
            first_line_of_schematics = True
            continue
        if first_line_of_schematics:
            lock_or_key = "lock" if all(i == "#" for i in line) else "key"
        schematic.append(list(line))
        first_line_of_schematics = False

    return locks, keys


def part1(input_file: TextIOWrapper):
    locks, keys = load_input(input_file)

    no_overlaps = 0
    for lock in locks:
        for key in keys:
            if VERBOSE:
                print(f"{lock=}, {key=}")
            no_overlaps += 1 if all((l + k <= 5) for l, k in zip(lock, key)) else 0

    print(f"Part 1: {no_overlaps:,}")


def part2(input_file: TextIOWrapper):
    wires, gates = load_input(input_file)


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
