import argparse
import collections
import concurrent.futures
import functools
import io
import itertools
import operator
import re
from collections import defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction
from io import TextIOWrapper
from pathlib import Path
from typing import NamedTuple

from rich import print
from tqdm.rich import tqdm, trange

VERBOSE = False

MAP_HEIGHT = 103
MAP_WIDTH = 101


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        if not (isinstance(other, Point) or isinstance(other, MutablePoint)):
            return NotImplemented
        return Point(self.x + other.x, self.y + other.y)


@dataclass
class MutablePoint:
    x: int
    y: int

    def __add__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        # NOTE!!!! special case of adding with wrapping around map edges!!!!
        return MutablePoint((self.x + other.x) % MAP_WIDTH, (self.y + other.y) % MAP_HEIGHT)

    def __iadd__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        self.x = (self.x + other.x) % MAP_WIDTH
        self.y = (self.y + other.y) % MAP_HEIGHT
        return self

    def __eq__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        return not self == other


@dataclass
class Robot:
    p: MutablePoint
    v: MutablePoint

    def move(self):
        self.p += self.v


def print_map(robots: list[Robot]):
    robot_positions = defaultdict(int)
    for r in robots:
        robot_positions[Point(r.p.x, r.p.y)] += 1

    print("    ", end="")
    for i in range(MAP_WIDTH):
        print(i % 10, end="")
    print("")
    for y in range(MAP_HEIGHT):
        print(f"{y:2}: ", end="")
        for x in range(MAP_WIDTH):
            if (count := robot_positions[Point(x, y)]) > 0:
                print(count, end="")
            else:
                print(".", end="")
        print("")
    print("")


def load_input(indata: TextIOWrapper) -> list[list[int]]:
    robot_re = re.compile(r"p=(?P<px>-?\d+),(?P<py>-?\d+) v=(?P<vx>-?\d+),(?P<vy>-?\d+)")
    robots = []
    for row_idx, line in enumerate(indata):
        line = line.split("#")[0].strip()
        if not line:
            continue
        if m := robot_re.match(line):
            robots.append(
                Robot(
                    MutablePoint(int(m.group("px")), int(m.group("py"))),
                    MutablePoint(int(m.group("vx")), int(m.group("vy"))),
                )
            )

    return robots


def part1(input_file: TextIOWrapper):
    part1_rounds = 100
    robots = load_input(input_file)
    if VERBOSE:
        print(robots)
    for round in range(part1_rounds):
        if VERBOSE:
            print(robots)
            print_map(robots)
        for r in robots:
            r.move()
    if VERBOSE:
        print(robots)
        print_map(robots)

    quadrant_counts = [[0, 0], [0, 0]]
    quadrants_x = [(0, MAP_WIDTH // 2), (MAP_WIDTH // 2 + 1, MAP_WIDTH)]
    quadrants_y = [(0, MAP_HEIGHT // 2), (MAP_HEIGHT // 2 + 1, MAP_HEIGHT)]
    for r in robots:
        if r.p.x == MAP_WIDTH // 2 or r.p.y == MAP_HEIGHT // 2:
            continue
        if r.p.x < MAP_WIDTH // 2:
            qx = 0
        else:
            qx = 1
        if r.p.y < MAP_HEIGHT // 2:
            qy = 0
        else:
            qy = 1
        quadrant_counts[qx][qy] += 1
    print(quadrant_counts)

    counts = [*quadrant_counts[0], *quadrant_counts[1]]
    safety_factor = functools.reduce(operator.mul, counts)
    print(f"Part 1: {safety_factor}")


def print_map2(robots: list[Robot], out_file):
    out = io.StringIO()
    robot_positions = defaultdict(int)
    for r in robots:
        robot_positions[Point(r.p.x, r.p.y)] += 1

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if (count := robot_positions[Point(x, y)]) > 0:
                print(count, end="", file=out)
            else:
                print(" ", end="", file=out)
        print("", file=out)
    print("", file=out)

    out_file.write(out.getvalue())


def part2(input_file: TextIOWrapper):
    part1_rounds = 1_000_000
    robots = load_input(input_file)
    with open("iterations dump2", "w") as out:
        for round in trange(1000, part1_rounds):
            print(f"\n\n\n\n\nIteration {round}", file=out)
            print_map2(robots, out)
            for r in robots:
                r.move()


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
