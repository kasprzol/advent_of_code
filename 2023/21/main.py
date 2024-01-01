import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence
from contextlib import suppress
import functools
import itertools
import tqdm
from rich import print


def part1():
    value = 0
    steps_to_take = 64

    walking_area = []
    # a map of point coordinates to the step number on which it was reached
    points_reached = {}
    for line in open("input.txt").readlines():
        line = line.strip()
        walking_area.append(line)
        with suppress(ValueError):
            idx = line.index("S")
            start = len(walking_area) - 1, idx

    area_h = len(walking_area)
    area_w = len(walking_area[0])

    possible_positions = [start]
    for step_no in tqdm.trange(1, steps_to_take + 1):
        new_possible_positions = []
        for step in possible_positions:
            for direction in ((-1, 0), (1, 0), (0, 1), (0, -1)):
                new_step = step[0] + direction[0], step[1] + direction[1]
                if (
                    new_step[0] < 0
                    or new_step[0] >= area_h
                    or new_step[1] < 0
                    or new_step[1] >= area_w
                    or walking_area[new_step[0]][new_step[1]] == "#"
                ):
                    continue
                if new_step not in points_reached:
                    points_reached[new_step] = step_no
                    new_possible_positions.append(new_step)
        possible_positions = new_possible_positions

    for step_no in points_reached.values():
        if step_no % 2 == 0:
            value += 1
    print(f"The value is {value}")


################################################################################


def part2():
    value = 0

    for line in open("input.txt").readlines():
        line = line.strip()

    print(f"The value is {value}")


if __name__ == "__main__":
    part1()
