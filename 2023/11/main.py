import dataclasses
import math
import re
from typing import NamedTuple
from collections.abc import Iterable, Sequence
import functools
import itertools
import tqdm
from rich import print


def print_sky(sky_map):
    for row in sky_map:
        r = "".join(row)
        r = r.replace("#", "[red]#[/red]")
        print(r)


def distance(p1, p2):
    return abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])


def part1():
    value = 0

    sky_map = []

    for line in open("input.txt").readlines():
        line = line.strip()
        sky_map.append(list(line))

    # print_sky(sky_map)
    print(f"The size of the map: {len(sky_map)}*{len(sky_map[0])}")

    rows_to_duplicate = []
    for r, row in enumerate(sky_map):
        if all(x == "." for x in row):
            rows_to_duplicate.append(r + len(rows_to_duplicate))

    columns_to_duplicate = []
    for c in range(len(sky_map[0])):
        if all(row[c] == "." for row in sky_map):
            columns_to_duplicate.append(c + len(columns_to_duplicate))

    for r in sky_map:
        for c in columns_to_duplicate:
            r.insert(c, r[c])
    for r in rows_to_duplicate:
        sky_map.insert(r, sky_map[r])

    # print_sky(sky_map)
    print(f"The size of the map: {len(sky_map)}*{len(sky_map[0])}")

    galaxies = {}
    for r, row in enumerate(sky_map):
        for c, col in enumerate(row):
            if col == "#":
                galaxies[len(galaxies) + 1] = (r, c)

    # print(galaxies)

    distances = {}

    for galaxy in tqdm.tqdm(galaxies):
        for other in range(galaxy + 1, len(galaxies) + 1):
            d = distance(galaxies[galaxy], galaxies[other])
            distances.setdefault(galaxy, {})[other] = d
            value += d

    # print(distances)

    print(f"The value is {value}")


################################################################################

EXPANSION_FACTOR = 1_000_000


def distance2(p1, p2, expanded_rows, expanded_cols):
    x1, x2 = p1[0], p2[0]
    if x1 > x2:
        x1, x2 = x2, x1
    y1, y2 = p1[1], p2[1]
    if y1 > y2:
        y1, y2 = y2, y1
    d = abs(x2 - x1) + abs(y2 - y1)
    for r in expanded_rows:
        if x1 < r < x2:
            d += EXPANSION_FACTOR - 1
    for c in expanded_cols:
        if y1 < c < y2:
            d += EXPANSION_FACTOR - 1
    return d


def part2():
    value = 0

    sky_map = []

    for line in open("input.txt").readlines():
        line = line.strip()
        sky_map.append(list(line))

    # print_sky(sky_map)
    print(f"The size of the map: {len(sky_map)}*{len(sky_map[0])}")

    rows_to_duplicate = []
    for r, row in enumerate(sky_map):
        if all(x == "." for x in row):
            rows_to_duplicate.append(r)

    columns_to_duplicate = []
    for c in range(len(sky_map[0])):
        if all(row[c] == "." for row in sky_map):
            columns_to_duplicate.append(c)
    print(f"{rows_to_duplicate=}, {columns_to_duplicate=}")

    # print_sky(sky_map)
    print(f"The size of the map: {len(sky_map)}*{len(sky_map[0])}")

    galaxies = {}
    for r, row in enumerate(sky_map):
        for c, col in enumerate(row):
            if col == "#":
                galaxies[len(galaxies) + 1] = (r, c)

    # print(galaxies)

    distances = {}

    for galaxy in tqdm.tqdm(galaxies):
        for other in range(galaxy + 1, len(galaxies) + 1):
            d = distance2(galaxies[galaxy], galaxies[other], rows_to_duplicate, columns_to_duplicate)
            distances.setdefault(galaxy, {})[other] = d
            value += d

    # print(distances)

    print(f"The value is {value}")


if __name__ == "__main__":
    part2()
