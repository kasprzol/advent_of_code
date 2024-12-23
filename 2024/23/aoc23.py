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
from tqdm import tqdm, trange

VERBOSE = False


def load_input(indata: TextIOWrapper):
    lines = []
    for row_idx, line in enumerate(indata):
        line = line.strip().split("#")[0]
        if not line:
            continue
        lines.append(line)
    return lines


def check_for_lan(node: str, computer_links: dict[str, set[str]]) -> set[frozenset[str]]:
    lans = set()
    neighbours = computer_links[node]
    for neighbour in neighbours:
        common_neighbours = computer_links[neighbour] & neighbours
        for cn in common_neighbours:
            lans.add(frozenset((node, neighbour, cn)))
    return lans


def filter_lans_with_letter_t(all_lans):
    ret = []
    for lan in all_lans:
        if any(computer.startswith("t") for computer in lan):
            ret.append(lan)
    return ret


def part1(input_file: TextIOWrapper):
    input_lines = load_input(input_file)
    computer_links = defaultdict(set)
    for link in input_lines:
        side_a, side_b = link.split("-")
        computer_links[side_a].add(side_b)
        computer_links[side_b].add(side_a)

    # solution
    all_lans = set()
    for node in computer_links:
        if len(computer_links[node]) < 2:
            continue
        lans_for_node = check_for_lan(node, computer_links)
        all_lans |= lans_for_node
    print_lans(all_lans)
    t_lans = filter_lans_with_letter_t(all_lans)
    print_lans(t_lans)
    result = len(t_lans)
    print(f"Part 1: {result:,}")


def print_lans(lans: frozenset[frozenset[str]]):
    sorted_sets = sorted([sorted(s) for s in lans])
    print(sorted_sets)


def part2(input_file: TextIOWrapper):
    secret_numbers = load_input(input_file)
    result = 0
    print(f"Part 2: {result:,}")


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
