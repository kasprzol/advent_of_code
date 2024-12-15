import argparse
import collections
import concurrent.futures
import enum
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


WALL = "#"
BOX = "O"
EMPTY = "."

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
        return MutablePoint(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        self.x += other.x
        self.y += other.y
        return self

    def __eq__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        return not self == other


class Direction(enum.StrEnum):
    UP = "^"
    DOWN = "v"
    LEFT = "<"
    RIGHT = ">"

DIRECTION_TO_VECTOR = {
    Direction.UP: Point(0, -1),
    Direction.DOWN: Point(0, 1),
    Direction.LEFT: Point(-1, 0),
    Direction.RIGHT: Point(1, 0),
        }


def print_map(warehouse, robots: list[MutablePoint]):
    robot_positions = defaultdict(int)
    for r in robots:
        robot_positions[Point(r.x, r.y)] += 1

    print("    ", end="")
    height = len(warehouse)
    width = len(warehouse[0])
    for i in range(width):
        print(i % 10, end="")
    print("")
    for y in range(height):
        print(f"{y:2}: ", end="")
        for x in range(width):
            if (count := robot_positions[Point(x, y)]) > 0:
                # print("\N{robot face}", end="")
                print("[red]@[/red]", end="")
            else:
                match warehouse[y][x]:
                    case "#":
                        print(f"[yellow]{WALL}[/yellow]", end="")
                    case "O":
                        print(f"[blue]{BOX}[/blue]", end="")
                    case _:
                        print(warehouse[y][x], end="")
        print("")
    print("")


def load_input(indata: TextIOWrapper):
    map = []
    moves = []
    robots = []
    reading_map = True
    for row_idx, line in enumerate(indata):
        line = line.strip()
        if not line:
            continue
        if "#" not in line:
            reading_map = False
        if reading_map:
            if "@" in line:
                col = line.index("@")
                assert line.count("@") == 1
                robots.append(MutablePoint(row_idx, col))
                line = line.replace("@", ".")
            map.append(list(line))
        else:
            moves.extend(list(line))
    return map, robots, moves


def move_robot(robot: MutablePoint, warehouse, direction: Direction) -> MutablePoint:
    """
    Try to move robot in the given direction. If there are boxes on the way then move them if possible by updating the
    warehouse. Return new (or old) robot position.
    """
    next_point = robot + DIRECTION_TO_VECTOR[direction]
    if warehouse[next_point.y][next_point.x] == WALL:
        return robot
    if warehouse[next_point.y][next_point.x] == EMPTY:
        return next_point
    # the robot is against a box - try to move it (and any other boxes behind it)
    boxes_to_move = [next_point]  # lets keep them all here, but in the end I just need to remove the last one and add one in the front
    point_to_check = MutablePoint(next_point.x, next_point.y)
    while True:
        point_to_check += DIRECTION_TO_VECTOR[direction]
        if warehouse[point_to_check.y][point_to_check.x] == WALL:
            return robot
        if warehouse[point_to_check.y][point_to_check.x] == EMPTY:
            # the robot can move the boxes in that direction
            # add a box at point_to_check and remove the first box from boxes_to_move
            warehouse[point_to_check.y][point_to_check.x] = BOX
            warehouse[boxes_to_move[0].y][boxes_to_move[0].x] = EMPTY
            return next_point
        boxes_to_move.append(point_to_check)
        

def part1(input_file: TextIOWrapper):
    warehouse, robots, robot_moves = load_input(input_file)
    robot_pos = robots[0]
    if VERBOSE:
        print_map(warehouse, [robot_pos])
    for move in tqdm(robot_moves):
        if VERBOSE:
            print(f"Move: [blue]{move}[/blue]")
        robot_pos = move_robot(robot_pos, warehouse, move)
        if VERBOSE:
            print_map(warehouse, [robot_pos])
    gps = 0
    for ridx, row in enumerate(warehouse):
        for cidx, c in enumerate(row):
            if c == BOX:
                gps += 100 * ridx + cidx
    print(f"Part 1: {gps}")




def part2(input_file: TextIOWrapper):
    print(f"Part 2: 0")


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
