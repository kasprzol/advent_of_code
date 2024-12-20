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
from io import TextIOWrapper
from pathlib import Path
from typing import Iterable, NamedTuple, TypedDict

from rich import print
from tqdm.rich import tqdm, trange

VERBOSE = False


class Point(NamedTuple):

    x: int
    y: int

    def __add__(self, other):
        if not (isinstance(other, Point) or isinstance(other, MutablePoint)):
            return NotImplemented
        return Point(self.x + other.x, self.y + other.y)

    def distance(self, other):
        if not (isinstance(other, Point)):  # or isinstance(other, MutablePoint)):
            raise NotImplementedError(f"Can't take distance of Point and {type(other)}")
        return abs(self.x - other.x) + abs(self.y - other.y)


class Direction(enum.StrEnum):
    UP = "^"
    DOWN = "v"
    LEFT = "<"
    RIGHT = ">"

    @staticmethod
    def values():
        return (Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT)

    # a dummy method to allow comparision
    def __lt__(self, other):
        if not isinstance(other, Direction):
            return NotImplemented
        return self.value < other.value

    def reverse(self):
        return DIRECTION_REVERSE[self.value]


DIRECTION_REVERSE = {
    "UP": Direction.DOWN,
    "DOWN": Direction.UP,
    "LEFT": Direction.RIGHT,
    "RIGHT": Direction.LEFT,
    "^": Direction.DOWN,
    "v": Direction.UP,
    "<": Direction.RIGHT,
    ">": Direction.LEFT,
}

DIRECTION_TO_VECTOR = {
    Direction.UP: Point(0, -1),
    Direction.DOWN: Point(0, 1),
    Direction.LEFT: Point(-1, 0),
    Direction.RIGHT: Point(1, 0),
}


@dataclass
class Region:
    name: str
    points: set[Point] = field(default_factory=set)
    perimeter: int = 0

    @property
    def area(self):
        return len(self.points)

    @property
    def price(self):
        return self.perimeter * self.area

    def is_connected(self, outside_point: Point):
        for point in self.points:
            if point.distance(outside_point) == 1:
                return True
        return False


def load_input(indata: TextIOWrapper):
    area = []
    region_names = set()
    for row_idx, line in enumerate(indata):
        line = line.split("#")[0].strip()
        if not line:
            continue
        area.append(list(line))
        region_names.update(line)
    return area, region_names


def find_regions(area) -> dict[str, list[Region]]:
    regions: dict[str, list[Region]] = {}
    area_h = len(area)
    area_w = len(area[0])
    for ridx, row in enumerate(area):
        for cidx, cell in enumerate(row):
            point = Point(x=cidx, y=ridx)
            same_name_neighbours = 0
            # Find a region of cell plants that is a neighbour of this point. If there is none, then create a new one.
            if cell not in regions:
                region = Region(name=cell)
                regions[cell] = [region]
            else:
                for r in reversed(regions[cell]):
                    if r.is_connected(point):
                        region = r
                        break
                else:
                    region = Region(name=cell)
                    regions[cell].append(region)

            for direction in Direction.values():
                neighbour = point + DIRECTION_TO_VECTOR[direction]
                if 0 <= neighbour.x < area_w and 0 <= neighbour.y < area_h:
                    if area[neighbour.y][neighbour.x] == cell:  # and neighbour not in regions[cell].points:
                        same_name_neighbours += 1
            point_perimeter = 4 - same_name_neighbours
            region.points.add(point)
            region.perimeter += point_perimeter
    return regions


def part1(input_file: TextIOWrapper):
    area, region_names = load_input(input_file)

    price = 0
    regions = find_regions(area)
    for name, small_regions in regions.items():
        for region in small_regions:
            if VERBOSE:
                print(f"Region {name}. Area: {region.area}\t perimeter: {region.perimeter}\tprice: {region.price}")
            price += region.price
    print(f"Part 1: {price:,}")


def part2(input_file: TextIOWrapper):
    patterns, designs = load_input(input_file)

    possible_designs = 0
    for design in tqdm(designs, desc="designs"):
        if number_of_combinations := make_design_from_patterns2(design):
            if VERBOSE:
                print(f"Number of combinations for design {design}: {number_of_combinations}")
            possible_designs += number_of_combinations

    print(f"Part 2: {possible_designs:,}")


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
