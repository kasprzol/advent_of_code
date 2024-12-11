import argparse
import functools
import itertools
from copy import deepcopy
from itertools import pairwise, combinations

from rich import print
from tqdm import trange, tqdm
from io import TextIOWrapper
from enum import Enum, StrEnum
import operator

VERBOSE = False

EMPTY = "."


def load_input(indata: TextIOWrapper):
    map = []
    antennas = {}
    for row_idx, line in enumerate(indata):
        map.append(list(line.strip()))
        for idx, i in enumerate(map[-1]):
            if i != EMPTY:
                antennas.setdefault(i, []).append((row_idx, idx))
    return map, antennas


def is_inside_map(point, map) -> bool:
    return 0 <= point[0] < len(map) and 0 <= point[1] < len(map[0])


def print_map(map, antinodes):
    print("    ", end="")
    for i in range(len(map[0])):
        print(i % 10, end="")
    print()
    for ridx, row in enumerate(map):
        print(f"{ridx:2}: ", end="")
        for cidx, cell in enumerate(row):
            if (ridx, cidx) in antinodes:
                print(f"[yellow]@[/yellow]", end="")
                continue
            if cell != EMPTY:
                print(f"[red]{cell}[/red]", end="")
                continue
            if cell == EMPTY:
                print(f"[white]{EMPTY}[/white]", end="")
                continue
        print("")
    print("")


def part1(input_file: TextIOWrapper):
    map, antennas = load_input(input_file)
    antinodes = set()
    for frequency in tqdm(antennas):
        for pair in tqdm(combinations(antennas[frequency], 2), leave=False):
            a, b = pair
            diff = (a[0] - b[0], a[1] - b[1])
            local_antinodes = {
                (a[0] + diff[0], a[1] + diff[1]),
                (b[0] - diff[0], b[1] - diff[1]),
            }
            local_antinodes_on_map = {i for i in local_antinodes if is_inside_map(i, map)}
            if VERBOSE:
                print(f"Antennas pair: {pair}. Antinodes: {local_antinodes}. {local_antinodes_on_map=} {diff=}")
                print_map(map, local_antinodes)
            antinodes |= local_antinodes_on_map

    print(f"part 1: {len(antinodes)}")


def part2(input_file: TextIOWrapper):
    map, antennas = load_input(input_file)
    antinodes = set()
    for frequency in tqdm(antennas):
        for pair in tqdm(combinations(antennas[frequency], 2), leave=False):
            a, b = pair
            antinodes |= {a, b}  # add antinodes at the antennas
            diff = (a[0] - b[0], a[1] - b[1])
            m = 0
            while True:
                m += 1
                local_antinodes = {
                    (a[0] + diff[0] * m, a[1] + diff[1] * m),
                    (b[0] - diff[0] * m, b[1] - diff[1] * m),
                }
                if all(not is_inside_map(antinode, map) for antinode in local_antinodes):
                    break
                local_antinodes_on_map = {i for i in local_antinodes if is_inside_map(i, map)}
                if VERBOSE:
                    print(f"Antennas pair: {pair}. Antinodes: {local_antinodes}. {local_antinodes_on_map=} {diff=}")
                    print_map(map, local_antinodes)
                antinodes |= local_antinodes_on_map

    print(f"part 2: {len(antinodes)}")


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
