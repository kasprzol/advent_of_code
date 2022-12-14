from ast import literal_eval
from collections import defaultdict
import heapq
from functools import cmp_to_key
from itertools import zip_longest, pairwise
from pprint import pprint
from typing import NamedTuple

ROCK = "#"
EMPTY = " "  # "."
SAND = "\N{LIGHT SHADE}"  # "o"
SAND_START = "+"
SAND_START_X = 500
SAND_START_Y = 0
NEW_SAND = "\N{FULL BLOCK}"


class Point(NamedTuple):
    x: int
    y: int


def print_cave(cave, cave_max_y, new_sand=None):
    min_x = min(cave.keys())
    max_x = max(cave.keys())
    print()
    for y in range(cave_max_y + 1):
        row = []
        for x in range(min_x, max_x + 1):
            if new_sand and new_sand.x == x and new_sand.y == y:
                row.append(NEW_SAND)
            else:
                row.append(cave[x][y])
        print(f"{y:2}", "".join(row))


def simulate_sand(cave, cave_min_x, cave_max_x, cave_max_y):
    print_cave(cave, cave_max_y)
    is_current_sand_moving = False
    reached_infinity = False
    active_sand = None
    units_of_sand = 0
    while not reached_infinity:
        if not is_current_sand_moving:
            units_of_sand += 1
            active_sand = Point(SAND_START_X, SAND_START_Y)
            is_current_sand_moving = True

        while cave[active_sand.x][active_sand.y + 1] == EMPTY:
            active_sand = Point(active_sand.x, active_sand.y + 1)
            if active_sand.y >= cave_max_y:
                print(units_of_sand - 1)
                return
                reached_infinity = True
                is_current_sand_moving = False
                break
        if reached_infinity:
            break
        # can move left-down?
        if cave[active_sand.x - 1][active_sand.y + 1] == EMPTY:
            active_sand = Point(active_sand.x - 1, active_sand.y + 1)
        # can move right-down?
        elif cave[active_sand.x + 1][active_sand.y + 1] == EMPTY:
            active_sand = Point(active_sand.x + 1, active_sand.y + 1)
        else:
            # the sand had rested
            cave[active_sand.x][active_sand.y] = SAND
            is_current_sand_moving = False
            print_cave(cave, cave_max_y, active_sand)


def part_1():
    segments = load_cave()
    cave = defaultdict(lambda: defaultdict(lambda: EMPTY))
    cave_min_x, cave_max_x, cave_max_y = 99999, 0, 0
    for segment in segments:
        for points in pairwise(segment):
            cave_min_x = min((cave_min_x, points[0].x, points[1].x))
            cave_max_x = max((cave_max_x, points[0].x, points[1].x))
            cave_max_y = max((cave_max_y, points[0].y, points[1].y))
            if points[0].x == points[1].x:
                min_y = min(points[0].y, points[1].y)
                max_y = max(points[0].y, points[1].y)
                for y in range(min_y, max_y + 1):
                    cave[points[0].x][y] = ROCK
            else:
                min_x = min(points[0].x, points[1].x)
                max_x = max(points[0].x, points[1].x)
                for x in range(min_x, max_x + 1):
                    cave[x][points[0].y] = ROCK
    cave[500][0] = SAND_START
    simulate_sand(cave, cave_min_x, cave_max_x, cave_max_y)


def load_cave() -> list[list[Point]]:
    segments: list[list[Point]] = []
    with open("input.txt") as indata:
        for line in indata:
            points_str = [p.split(",") for p in line.strip().split(" -> ")]
            points = [Point(int(x), int(y)) for x, y in points_str]
            segments.append(points)
    return segments


def part_2():
    ...


if __name__ == "__main__":
    part_1()
