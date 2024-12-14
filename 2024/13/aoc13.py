import argparse
import collections
import concurrent.futures
import itertools
import re
from collections import deque
from fractions import Fraction
from io import TextIOWrapper
from typing import NamedTuple

from rich import print
from tqdm.rich import tqdm, trange

VERBOSE = False

TOP_HEIGHT = 9


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        if not (isinstance(other, Point) or isinstance(other, MutablePoint)):
            return NotImplemented
        return Point(self.x + other.x, self.y + other.y)


class ClawMachine(NamedTuple):
    button_a: Point
    button_b: Point
    prize: Point


def load_input(indata: TextIOWrapper) -> list[list[int]]:
    button_re = re.compile(r"Button (?P<button>A|B): X\+(?P<x>\d+), Y\+(?P<y>\d+)")
    prize_re = re.compile(r"Prize: X=(?P<x>\d+), Y=(?P<y>\d+)")
    buttons = []
    claws = []
    for row_idx, line in enumerate(indata):
        line = line.split("#")[0].strip()
        if not line:
            continue
        if m := button_re.match(line):
            buttons.append(Point(int(m.group("x")), int(m.group("y"))))
        elif m := prize_re.match(line):
            prize = Point(int(m.group("x")), int(m.group("y")))
            claws.append(ClawMachine(buttons[0], buttons[1], prize))
            buttons = []

    return claws


def part1(input_file: TextIOWrapper):
    claws = load_input(input_file)
    if VERBOSE:
        print(claws)
    tokens = 0
    tokens_per_a = 3
    tokens_per_b = 1
    for claw in claws:
        # just 2 equations with 2 unknowns
        s = claw.button_a.x
        t = claw.button_b.x
        u = claw.prize.x
        x = claw.button_a.y
        y = claw.button_b.y
        z = claw.prize.y
        b = (Fraction(z * s, 1) - Fraction(u * x, 1)) / (Fraction(y * s, 1) - t * x)
        a = (Fraction(u, 1) - b * t) / s
        print(f"{a=}, {b=}")
        if a.is_integer() and b.is_integer():
            tokens += int(a) * tokens_per_a + int(b) * tokens_per_b

    print(f"Part 1: {tokens}")


def part2(input_file: TextIOWrapper):
    claws = load_input(input_file)
    if VERBOSE:
        print(claws)
    tokens = 0
    tokens_per_a = 3
    tokens_per_b = 1
    for claw in claws:
        # just 2 equations with 2 unknowns
        s = claw.button_a.x
        t = claw.button_b.x
        u = claw.prize.x + 10000000000000
        x = claw.button_a.y
        y = claw.button_b.y
        z = claw.prize.y + 10000000000000
        b = (Fraction(z * s, 1) - Fraction(u * x, 1)) / (Fraction(y * s, 1) - t * x)
        a = (Fraction(u, 1) - b * t) / s
        print(f"{a=}, {b=}")
        if a.is_integer() and b.is_integer():
            tokens += int(a) * tokens_per_a + int(b) * tokens_per_b

    print(f"Part 2: {tokens}")


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
