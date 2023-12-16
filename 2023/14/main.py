import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence
import functools
import itertools
import tqdm
from rich import print
from tqdm.rich import trange

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
    tilt_north(area)
    value = calculate_load(area)

    print(f"The value is {value}")


################################################################################


def horizontal_enumerator(row, direction):
    if direction == "E":
        h = len(row)
        for idx, it in enumerate(reversed(row), 1):
            yield h - idx, it
    else:
        yield from enumerate(row)


def vertical_enumerator(area, direction):
    if direction == "S":
        h = len(area)
        for idx, it in enumerate(reversed(area), 1):
            yield h - idx, it
    else:
        yield from enumerate(area)


def tilt(area, direction):
    rocks_moved = True
    area_h = len(area)
    area_w = len(area[0])
    match direction:
        case "N":
            direction_horizontal = 0
            direction_vertical = -1
        case "S":
            direction_horizontal = 0
            direction_vertical = 1
        case "W":
            direction_horizontal = -1
            direction_vertical = 0
        case "E":
            direction_horizontal = 1
            direction_vertical = 0
    while rocks_moved:
        # print_area(area)
        rocks_moved = False
        for r, row in vertical_enumerator(area, direction):
            if r + direction_vertical < 0 or r + direction_vertical == area_h:
                continue
            for c, space in horizontal_enumerator(row, direction):
                if c + direction_horizontal < 0 or c + direction_horizontal == area_w or space != MOVEABLE:
                    continue
                if direction in ("N", "S"):
                    i = r + direction_vertical
                    while area[i][c] == EMPTY:
                        new_i = i + direction_vertical
                        if (0 <= new_i < area_h) and area[new_i][c] == EMPTY:
                            i += direction_vertical
                        else:
                            break
                    if area[i][c] == EMPTY:
                        area[i][c], row[c] = space, EMPTY
                        rocks_moved = True
                else:
                    i = c + direction_horizontal
                    while area[r][i] == EMPTY:
                        new_i = i + direction_horizontal
                        if (0 <= new_i < area_w) and area[r][new_i] == EMPTY:
                            i += direction_horizontal
                        else:
                            break
                    if area[r][i] == EMPTY:
                        area[r][i], row[c] = space, EMPTY
                        rocks_moved = True
            if rocks_moved:
                break


CYCLES = 1_000_000_000


def checksum(area):
    import hashlib

    h = hashlib.sha256()
    for row in area:
        h.update("".join(row).encode())
    return h.hexdigest()


def part2():
    value = 0
    from collections import defaultdict

    area = read_input()
    seen_hashes = defaultdict(list)
    for i in trange(1, CYCLES + 1, unit_scale=True):
        tilt(area, "N")
        tilt(area, "W")
        tilt(area, "S")
        tilt(area, "E")
        # print(f"After {i+1} cycles:")
        # print_area(area)
        if i > 1_000:
            h = checksum(area)
            seen_hashes[h].append(i)
            if len(seen_hashes[h]) > 100:
                print(f"Iterations for hash={h}: {seen_hashes[h]}")
                break
    print(seen_hashes.keys())
    derivatives = [b - a for a, b in itertools.pairwise(seen_hashes[h])]
    # print(derivatives)
    derivatives = set(derivatives)
    print(derivatives)
    assert len(derivatives) == 1
    derivative = derivatives.pop()
    cycles_left = CYCLES - i
    loops_left = cycles_left // derivative
    for j in trange(i + loops_left * derivative, CYCLES):
        tilt(area, "N")
        tilt(area, "W")
        tilt(area, "S")
        tilt(area, "E")
        value = calculate_load(area)
        print(f"{j=}, {value=}")

    print(f"The value is {value}")


if __name__ == "__main__":
    part2()
