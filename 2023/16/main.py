import re
import dataclasses
import enum
from typing import NamedTuple
from collections.abc import Iterable, Sequence
from collections import defaultdict
import functools
import itertools
import tqdm
from rich import print
from rich.console import Console
from rich.text import Text


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
        self.path.append(self.p)

    def set_point(self, new_p: Point):
        new_path_segment = new_p
        self.path.append(new_path_segment)
        self.p = new_p


rotation = {
    Direction.UP: {"/": Direction.RIGHT, "\\": Direction.LEFT},
    Direction.DOWN: {"/": Direction.LEFT, "\\": Direction.RIGHT},
    Direction.RIGHT: {"/": Direction.UP, "\\": Direction.DOWN},
    Direction.LEFT: {"/": Direction.DOWN, "\\": Direction.UP},
}


console = Console(highlight=False)


def print_ray(ray: Ray, cave, energized_tiles):
    cave = [list(row) for row in cave]
    for tile in energized_tiles:
        cave[tile.r][tile.c] = "[yellow]#[/yellow]"
    for p in ray.path:
        cave[p.r][p.c] = "[red]@[/red]"
    cave[p.r][p.c] = "[bright_magenta]*[/bright_magenta]"

    nums = "".join(f"{i}         " for i in range(len(cave[0]) // 10))
    print(f"     {nums}")
    nums = "01234567890" * (len(cave[0]) // 10)
    print(f"     {nums}")
    for row_idx, row in enumerate(cave):
        # avoid problem with rich like "\[red]"
        row = "".join(row).replace("\\", "\u2572")
        # .replace("/", "\u2571")
        console.print(f"{row_idx:3}: {row}")
    print("")


def trace_light(cave: list[str]) -> int:
    active_rays = [Ray(Point(0, 0), Direction.RIGHT)]
    cave_h = len(cave)
    cave_w = len(cave[0])
    energized_tiles = defaultdict(set)
    energized_tiles[Point(0, 0)] = {Direction.RIGHT}
    while active_rays:
        ray = active_rays.pop()
        # print_ray(ray, cave, energized_tiles)
        print(f"active_rays: {len(active_rays)}")
        while True:
            tile = cave[ray.p.r][ray.p.c]
            energized_tiles[ray.p].add(ray.direction)
            if tile in ("/", "\\"):
                ray.direction = rotation[ray.direction][tile]
            elif tile in ("-", "|"):
                if not (
                    (tile == "|" and ray.direction in (Direction.UP, Direction.DOWN))
                    or (tile == "-" and ray.direction in (Direction.LEFT, Direction.RIGHT))
                ):
                    if tile == "|":
                        ray.direction = Direction.DOWN
                        active_rays.append(Ray(ray.p, Direction.UP, path=ray.path.copy()))
                    else:
                        ray.direction = Direction.RIGHT
                        active_rays.append(Ray(ray.p, Direction.LEFT, path=ray.path.copy()))

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
            if next_point in energized_tiles and ray.direction in energized_tiles[next_point]:
                # we have already visited this tile in this direction - skip it
                break
            ray.set_point(next_point)

    # print(energized_tiles)
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
