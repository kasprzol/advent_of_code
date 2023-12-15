import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence
import functools
import itertools
import tqdm
from rich import print

MOVEABLE = "O"
STATIONARY = "#"
EMPTY = "."


def read_input():
    area = []
    for line in open("input.txt").readlines():
        line = line.strip()
        area.append(list(line))
    return area


def print_area(area):
    for r, row in enumerate(area):
        row = "".join(row)
        row = row.replace(MOVEABLE, f"[blue]{MOVEABLE}[/blue]")
        row = row.replace(STATIONARY, f"[red]{STATIONARY}[/red]")
        row = row.replace(EMPTY, f"[gray]{EMPTY}[/gray]")
        print(f"{r:3}: {row}")
    print("")


def tilt_north(area):
    rocks_moved = True
    while rocks_moved:
        print_area(area)
        rocks_moved = False
        for r, row in enumerate(area[1:], 1):
            for c, space in enumerate(row):
                if space == MOVEABLE:
                    i = r - 1
                    while True:
                        if area[i][c] != EMPTY:
                            break
                        if i > 0:
                            if area[i - 1][c] == EMPTY:
                                i -= 1
                            else:
                                break
                        else:
                            break
                    # i == -1 means we searched all above rows and all were empty
                    if i == -1 or (i >= 0 and area[i][c] == EMPTY):
                        area[max(i, 0)][c], row[c] = space, EMPTY
                        rocks_moved = True
            if rocks_moved:
                break


def calculate_load(area) -> int:
    area_height = len(area)
    load = 0
    for r, row in enumerate(area):
        for c in row:
            if c == MOVEABLE:
                load += area_height - r
    return load


def part1():
    value = 0

    area = read_input()
    print_area(area)
    tilt_north(area)
    print("")
    print_area(area)
    value = calculate_load(area)

    print(f"The value is {value}")


################################################################################


def part2():
    value = 0

    for line in open("input.txt").readlines():
        line = line.strip()

    print(f"The value is {value}")


if __name__ == "__main__":
    part1()
