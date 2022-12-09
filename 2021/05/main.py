from collections import Counter, defaultdict

from dataclasses import dataclass
import re


@dataclass
class Point:
    x: int
    y: int


def part_1():
    lines = []
    r = re.compile(r"(\d+),(\d+) -> (\d+),(\d+)")
    with open("input.txt") as indata:
        for line in indata:
            m = r.match(line)
            start_x, start_y, end_x, end_y = m[1], m[2], m[3], m[4]
            start = Point(int(start_x), int(start_y))
            end = Point(int(end_x), int(end_y))
            lines.append((start, end))

    grid = defaultdict(lambda: defaultdict(int))
    for line in lines:
        # For now, only consider horizontal and vertical lines: lines where either x1 = x2 or y1 = y2.
        if line[0].x == line[1].x:
            for y in range(min(line[0].y, line[1].y), max(line[0].y, line[1].y) + 1):
                grid[line[0].x][y] += 1
        else:
            for x in range(min(line[0].x, line[1].x), max(line[0].x, line[1].x) + 1):
                grid[x][line[0].y] += 1

    num_of_at_least_2 = 0
    for row in grid:
        for col in grid[row]:
            if grid[row][col] >= 2:
                num_of_at_least_2 += 1
            print(f"x={row},y={col}, num of lines: {grid[row][col]}")
    print(num_of_at_least_2)


def part_2():
    lines = []
    r = re.compile(r"(\d+),(\d+) -> (\d+),(\d+)")
    with open("input.txt") as indata:
        for line in indata:
            m = r.match(line)
            start_x, start_y, end_x, end_y = m[1], m[2], m[3], m[4]
            start = Point(int(start_x), int(start_y))
            end = Point(int(end_x), int(end_y))
            lines.append((start, end))

    grid = defaultdict(lambda: defaultdict(int))
    for line in lines:
        # For now, only consider horizontal and vertical lines: lines where either x1 = x2 or y1 = y2.
        if line[0].x == line[1].x:
            for y in range(min(line[0].y, line[1].y), max(line[0].y, line[1].y) + 1):
                grid[line[0].x][y] += 1
        elif line[0].y == line[1].y:
            for x in range(min(line[0].x, line[1].x), max(line[0].x, line[1].x) + 1):
                grid[x][line[0].y] += 1
        else:  # daigonal
            ...

    num_of_at_least_2 = 0
    for row in grid:
        for col in grid[row]:
            if grid[row][col] >= 2:
                num_of_at_least_2 += 1
            print(f"x={row},y={col}, num of lines: {grid[row][col]}")
    print(num_of_at_least_2)


if __name__ == '__main__':
    part_2()
    part_2()
