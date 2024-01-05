import ast
import dataclasses
import functools
import itertools
import re
from collections.abc import Iterable, Sequence
from typing import NamedTuple

import tqdm
from rich import print

EMPTY = "."


@dataclasses.dataclass
class Point3d:
    x: int
    y: int
    z: int


@dataclasses.dataclass
class Brick:
    start: Point3d
    end: Point3d
    number: int = -1

    # order bricks by their distance from the ground
    def __lt__(self, other: tuple[Point3d, ...]) -> bool:
        my_lowest = min(self.start, self.end, key=lambda x: x.z)
        their_lowest = min(other.start, other.end, key=lambda x: x.z)
        return my_lowest.z < their_lowest.z

    def direction(self):
        """Return the axis in which the brick extends."""
        if self.start.x != self.end.x:
            return "x"
        elif self.start.y != self.end.y:
            return "y"
        return "z"


def load_bricks():
    bricks = []
    area_x, area_y, area_z = 0, 0, 0
    for line in open("input.txt").readlines():
        line = line.strip()
        start, end = line.split("~")
        b = Brick(Point3d(*ast.literal_eval(start)), end=Point3d(*ast.literal_eval(end)))
        bricks.append(b)
        if (bx := max(b.start.x, b.end.x)) > area_x:
            area_x = bx
        if (by := max(b.start.y, b.end.y)) > area_y:
            area_y = by
        if (bz := max(b.start.z, b.end.z)) > area_z:
            area_z = bz
        assert b.start.z <= b.end.z

    return bricks, (area_x, area_y, area_z)


def dump_bricks(bricks: list[Brick], area):
    for brick in bricks:
        new_z = brick.start.z
        range_x = list(range(brick.start.x, brick.end.x + 1))
        range_y = list(range(brick.start.y, brick.end.y + 1))
        for test_z in range(brick.start.z - 1, 0, -1):
            if all(area[test_x][test_y][test_z] == EMPTY for test_x in range_x for test_y in range_y):
                new_z = test_z
            else:
                break
        diff_z = brick.start.z - new_z
        brick.start.z -= diff_z
        brick.end.z -= diff_z

        for x in range_x:
            for y in range_y:
                for z in range(brick.start.z, brick.end.z + 1):
                    area[x][y][z] = brick.number

    return area


def can_brick_be_removed(brick_to_be_removed: Brick, bricks: list[Brick], area) -> bool:
    """Given already settled bricks try to dump them again, this time assuming that the given brick
    does not exist."""
    empty_space = (EMPTY, brick_to_be_removed.number)
    for brick in bricks:
        if brick == brick_to_be_removed:
            continue
        new_z = brick.start.z
        range_x = list(range(brick.start.x, brick.end.x + 1))
        range_y = list(range(brick.start.y, brick.end.y + 1))
        for test_z in range(brick.start.z - 1, 0, -1):
            if all(area[test_x][test_y][test_z] in empty_space for test_x in range_x for test_y in range_y):
                # a brick moved.
                return False
            else:
                break

    return True


def part1():
    value = 0

    bricks, area_size = load_bricks()
    area = [[[EMPTY] * (area_size[2] + 1) for y in range(area_size[1] + 1)] for x in range(area_size[0] + 1)]

    print(bricks)
    # now bricks are sorted from lowest to highest
    bricks.sort()
    print(bricks)
    for idx, brick in enumerate(bricks, 1):
        brick.number = idx

    dump_bricks(bricks, area)

    for brick in bricks:
        if can_brick_be_removed(brick, bricks, area):
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
