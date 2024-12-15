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

    def copy(self):
        return MutablePoint(self.x, self.y)


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


def print_map(warehouse, robot: MutablePoint):
    print("    ", end="")
    height = len(warehouse)
    width = len(warehouse[0])
    for i in range(width):
        print(i % 10, end="")
    print("")
    for y in range(height):
        print(f"{y:2}: ", end="")
        for x in range(width):
            if robot == Point(x, y):
                # print("\N{robot face}", end="")
                print("[red]@[/red]", end="")
            else:
                match warehouse[y][x]:
                    case "#":
                        print(f"[yellow]{WALL}[/yellow]", end="")
                    case w if w in (BOX, "[", "]"):
                        print(f"[blue]{w}[/blue]", end="")
                    case _:
                        print(warehouse[y][x], end="")
        print("")
    print("")


def load_input(indata: TextIOWrapper):
    map = []
    moves = []
    robot = None
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
                robot = MutablePoint(row_idx, col)
                line = line.replace("@", ".")
            map.append(list(line))
        else:
            moves.extend(list(line))
    return map, robot, moves


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
    boxes_to_move = [
        next_point
    ]  # lets keep them all here, but in the end I just need to remove the last one and add one in the front
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
    warehouse, robot_pos, robot_moves = load_input(input_file)
    if VERBOSE:
        print_map(warehouse, robot_pos)
    for move in (robot_moves):
        if VERBOSE:
            print(f"Move: [blue]{move}[/blue]")
        robot_pos = move_robot(robot_pos, warehouse, move)
        if VERBOSE:
            print_map(warehouse, robot_pos)
    gps = 0
    for ridx, row in enumerate(warehouse):
        for cidx, c in enumerate(row):
            if c == BOX:
                gps += 100 * ridx + cidx
    print(f"Part 1: {gps}")


def load_input2(indata: TextIOWrapper):
    map = []
    moves = []
    robot = None
    reading_map = True
    for row_idx, line in enumerate(indata):
        line = line.strip()
        map_row = []
        if not line:
            continue
        if "#" not in line:
            reading_map = False
        if reading_map:
            for point in line:
                match point:
                    case "#":
                        map_row.extend(["#", "#"])
                    case "O":
                        map_row.extend(["[", "]"])
                    case ".":
                        map_row.extend([".", "."])
                    case "@":
                        map_row.extend([".", "."])
                        robot = MutablePoint(len(map_row) - 2, row_idx)
            map.append(map_row)

        else:
            moves.extend(list(line))
    return map, robot, moves


def can_move_box_vertical(box_left, warehouse, direction: Direction) -> bool | list[MutablePoint]:
    # if true, return a list of boxes that have to be moved
    ret = []
    for source in (box_left, box_left + DIRECTION_TO_VECTOR[Direction.RIGHT]):
        dest = source + DIRECTION_TO_VECTOR[direction]
        destination_value = warehouse[dest.y][dest.x]
        if destination_value == WALL:
            return False
        if destination_value == EMPTY:
            ret.append(source.copy())
        elif destination_value == "[":
            if r := can_move_box_vertical(dest, warehouse, direction):
                for i in r:
                    if i not in ret:
                        ret.append(i)
                ret.append(source.copy())
            else:
                return r
        else:
            d = dest + DIRECTION_TO_VECTOR[Direction.LEFT]
            if r := can_move_box_vertical(d, warehouse, direction):
                for i in r:
                    if i not in ret:
                        ret.append(i)
                ret.append(source.copy())
            else:
                return r
    return ret if ret else False


def move_robot2(robot: MutablePoint, warehouse, direction: Direction) -> MutablePoint:
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
    boxes_to_move = [
        next_point
    ]  # lets keep them all here, but in the end I just need to remove the last one and add one in the front
    point_to_check = MutablePoint(next_point.x, next_point.y)
    if direction in (Direction.LEFT, Direction.RIGHT):
        # trival case
        while True:
            point_to_check += DIRECTION_TO_VECTOR[direction]
            if warehouse[point_to_check.y][point_to_check.x] == WALL:
                return robot
            if warehouse[point_to_check.y][point_to_check.x] == EMPTY:
                # the robot can move the boxes in that direction
                # TODO: now have to move all the boxes, as those consist of 2 parts.
                warehouse[point_to_check.y][point_to_check.x] = warehouse[boxes_to_move[-1].y][boxes_to_move[-1].x]
                for box1, box2 in itertools.pairwise(reversed(boxes_to_move)):
                    warehouse[box1.y][box1.x] = warehouse[box2.y][box2.x]
                warehouse[boxes_to_move[0].y][boxes_to_move[0].x] = EMPTY
                return next_point
            boxes_to_move.append(point_to_check.copy())
    else:
        # move boxes up or down
        dest = (
            next_point
            if warehouse[next_point.y][next_point.x] == "["
            else next_point + DIRECTION_TO_VECTOR[Direction.LEFT]
        )
        boxes_to_move = can_move_box_vertical(dest, warehouse, direction)
        if boxes_to_move is False:
            return robot
        else:
            for box in boxes_to_move:
                dest = box + DIRECTION_TO_VECTOR[direction]
                warehouse[dest.y][dest.x] = warehouse[box.y][box.x]
                warehouse[box.y][box.x] = EMPTY
            return next_point


def part2(input_file: TextIOWrapper):
    warehouse, robot, robot_moves = load_input2(input_file)
    if VERBOSE:
        print_map(warehouse, robot)
    for midx, move in enumerate(robot_moves):
        if VERBOSE:
            print(f"Move {midx}: [blue]{move}[/blue]")
        robot = move_robot2(robot, warehouse, move)
        assert warehouse[robot.y][robot.x] == EMPTY
        if VERBOSE:
            print_map(warehouse, robot)
    gps = 0
    for ridx, row in enumerate(warehouse):
        for cidx, c in enumerate(row):
            if c == "[":
                gps += 100 * ridx + cidx
    print(f"Part 2: {gps}")


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
