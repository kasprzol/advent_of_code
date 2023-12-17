import re
import dataclasses
import enum
from typing import NamedTuple
from collections.abc import Iterable, Sequence
import functools
import itertools
import tqdm
from rich import print


class Point(NamedTuple):
    r: int
    c: int

    # def __add__(self, other):
    #     if not (isinstance(other, Point) or isinstance(other, MutablePoint)):
    #         return NotImplemented
    #     return Point(self.x + other.x, self.y + other.y)


class Direction(enum.StrEnum):
    UP = "U"
    DOWN = "D"
    RIGHT = "R"
    LEFT = "L"


@dataclasses.dataclass
class Ray:
    p: Point
    direction: Direction
    path: list[tuple[Point, Direction]] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        self.path.append((self.p, self.direction))

    def set_point(self, new_p: Point):
        new_path_segment = (new_p, self.direction)
        if new_path_segment in self.path:
            raise PointAlreadyInPathError()
        self.path.append(new_path_segment)
        self.p = new_p


rotation = {
    Direction.UP: {"/": Direction.RIGHT, "\\": Direction.LEFT},
    Direction.DOWN: {"/": Direction.LEFT, "\\": Direction.RIGHT},
    Direction.RIGHT: {"/": Direction.UP, "\\": Direction.DOWN},
    Direction.LEFT: {"/": Direction.DOWN, "\\": Direction.UP},
}


class PointAlreadyInPathError(Exception):
    pass


def print_ray(ray: Ray, cave, energized_tiles):
    from copy import deepcopy

    cave = [list(row) for row in cave]
    for tile in energized_tiles:
        cave[tile.r][tile.c] = "[yellow]#[/yellow]"
    for p, _ in ray.path:
        cave[p.r][p.c] = "[red]@[/red]"
    cave[p.r][p.c] = "[bright_magenta]*[/bright_magenta]"

    for row_idx, row in enumerate(cave):
        # avoid problem with rich like "\[red]"
        row = "".join(row).replace("\\", "\\\\")
        print(f"{row_idx:3}: {row}")
    print("")


def trace_light(cave: list[str]) -> int:
    active_rays = [Ray(Point(0, 0), Direction.RIGHT)]
    cave_h = len(cave)
    cave_w = len(cave[0])
    energized_tiles = {Point(0, 0)}
    while active_rays:
        ray = active_rays.pop()
        print_ray(ray, cave, energized_tiles)
        while True:
            match ray.direction:
                case Direction.UP:
                    next_point = Point(ray.p.r - 1, ray.p.c)
                case Direction.DOWN:
                    next_point = Point(ray.p.r + 1, ray.p.c)
                case Direction.RIGHT:
                    next_point = Point(ray.p.r, ray.p.c + 1)
                case Direction.LEFT:
                    next_point = Point(ray.p.r, ray.p.c - 1)
            if next_point.r < 0 or next_point.r >= cave_w or next_point.c < 0 or next_point.c >= cave_h:
                # light ray hit the cave wall
                break
            tile = cave[next_point.r][next_point.c]
            energized_tiles.add(next_point)
            try:
                ray.set_point(next_point)
            except PointAlreadyInPathError:
                break
            if tile == ".":
                continue
            elif tile in ("/", "\\"):
                ray.direction = rotation[ray.direction][tile]
            else:  # "-" or "|"
                if (tile == "|" and ray.direction in (Direction.UP, Direction.DOWN)) or (
                    tile == "-" and ray.direction in (Direction.LEFT, Direction.RIGHT)
                ):
                    continue
                if tile == "|":
                    new_directions = (Direction.UP, Direction.DOWN)
                else:
                    new_directions = (Direction.RIGHT, Direction.LEFT)
                for d in new_directions:
                    active_rays.append(Ray(ray.p, d, path=ray.path.copy()))
                break
    print(energized_tiles)
    return len(energized_tiles)


def part1():
    value = 0

    cave = []
    for line in open("input.txt").readlines():
        line = line.strip()
        cave.append(line)

    value = trace_light(cave)

    print(f"The value is {value}")


################################################################################


def part2():
    value = 0

    for line in open("input.txt").readlines():
        line = line.strip()

    print(f"The value is {value}")


if __name__ == "__main__":
    part1()
