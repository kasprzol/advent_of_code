import dataclasses
import enum
import functools
import itertools
import re
from collections.abc import Iterable, Sequence
from typing import NamedTuple

import tqdm
from rich import print


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        if not (isinstance(other, Point) or isinstance(other, MutablePoint)):
            return NotImplemented
        return Point(self.x + other.x, self.y + other.y)


class Direction(enum.Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    NORTH = "UP"
    SOUTH = "DOWN"
    EAST = "RIGHT"
    WEST = "LEFT"

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


DIRECTION_REVERSE = {"UP": Direction.DOWN, "DOWN": Direction.UP, "LEFT": Direction.RIGHT, "RIGHT": Direction.LEFT}


DIRECTION_TO_VECTOR = {
    Direction.UP: Point(0, -1),
    Direction.DOWN: Point(0, 1),
    Direction.LEFT: Point(-1, 0),
    Direction.RIGHT: Point(1, 0),
}


# | is a vertical pipe connecting north and south.
# - is a horizontal pipe connecting east and west.
# L is a 90-degree bend connecting north and east.
# J is a 90-degree bend connecting north and west.
# 7 is a 90-degree bend connecting south and west.
# F is a 90-degree bend connecting south and east.
# . is ground; there is no pipe in this tile.
# S is the starting position of the animal; there is a pipe on this tile, but your sketch doesn't show what shape the pipe has.

POSSIBLE_CONNECTIONS = {
    Direction.LEFT: {"-": Direction.LEFT, "L": Direction.UP, "F": Direction.DOWN},
    Direction.RIGHT: {"-": Direction.RIGHT, "J": Direction.UP, "7": Direction.DOWN},
    Direction.UP: {"|": Direction.UP, "F": Direction.RIGHT, "7": Direction.LEFT},
    Direction.DOWN: {"|": Direction.DOWN, "L": Direction.RIGHT, "J": Direction.LEFT},
}


@dataclasses.dataclass
class Branch:
    current_point: Point
    direction: Direction
    distance: int = 1
    visited_points: set = dataclasses.field(default_factory=set, init=False)

    def __post_init__(self):
        self.visited_points.add(self.current_point)


def make_1_move(branch: Branch, maze):
    next_direction = POSSIBLE_CONNECTIONS[branch.direction][maze[branch.current_point.y][branch.current_point.x]]
    next_point = branch.current_point + DIRECTION_TO_VECTOR[next_direction]
    branch.distance += 1
    branch.visited_points.add(next_point)
    branch.current_point = next_point
    branch.direction = next_direction
    # print(branch)


def part1():
    value = 0
    maze = []
    start = None

    for row, line in enumerate(open("input.txt").readlines()):
        line = line.strip()
        maze.append(list(line))
        if "S" in maze[-1]:
            start = Point(y=row, x=maze[-1].index("S"))

    print(maze)
    maze_h = len(maze)
    maze_w = len(maze[0])

    # find loop segments connected to start
    loop_branches: list[Branch] = []
    for direction in Direction.values():
        p = start + DIRECTION_TO_VECTOR[direction]
        if p.y < 0 or p.y >= maze_h or p.x < 0 or p.x >= maze_w:
            continue
        if (pipe_element := maze[p.y][p.x]) in POSSIBLE_CONNECTIONS[direction]:
            # found one of the loop segments connected to the start
            print(f"Found {pipe_element} at {p=}")
            loop_branches.append(Branch(p, direction))

    print(loop_branches)
    while loop_branches[0].current_point != loop_branches[1].current_point:
        make_1_move(loop_branches[0], maze)
        make_1_move(loop_branches[1], maze)
    value = loop_branches[0].distance
    print(f"The value is {value}")


################################################################################


def part2():
    value = 0

    for line in open("input.txt").readlines():
        line = line.strip()

    print(f"The value is {value}")


if __name__ == "__main__":
    part1()
