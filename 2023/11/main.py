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


def part2():
    value = 0

    for line in open("input.txt").readlines():
        line = line.strip()

    print(f"The value is {value}")


if __name__ == "__main__":
    part1()
