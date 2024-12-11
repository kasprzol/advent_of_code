import collections
import itertools
from collections import deque
from io import TextIOWrapper
from typing import NamedTuple
import concurrent.futures
from rich import print
from tqdm.rich import tqdm

VERBOSE = False

TOP_HEIGHT = 9


def load_input(indata: TextIOWrapper) -> list[list[int]]:
    topo_map = []
    for row_idx, line in enumerate(indata):
        line = line.split("#")[0].strip()
        if not line:
            continue
        blocks = [int(i) for i in line]
        topo_map.append(blocks)
    return topo_map


import argparse


class Point2D(NamedTuple):
    r: int
    c: int


def print_map(topo_map: list[list[int]], trail_points: list[Point2D]) -> None:
    print(f"    ", end="")
    for i in range(len(topo_map[0])):
        print(f"[grey]{i % 10}[/grey]", end="")
    print("")
    for row_idx, row in enumerate(topo_map):
        print(f"[grey]{row_idx:2}:[/grey] ", end="")
        for col_idx, val in enumerate(row):
            if (row_idx, col_idx) in trail_points:
                print("[red]@[/red]", end="")
            else:
                print(topo_map[row_idx][col_idx], end="")
        print("")
    print("")


def get_neighbours(point: Point2D, topo_map) -> list[Point2D]:
    ret = []
    point_height = topo_map[point.r][point.c]
    if point.r > 0 and topo_map[point.r - 1][point.c] == point_height + 1:
        ret.append(Point2D(point.r - 1, point.c))
    if point.r < len(topo_map) - 1 and topo_map[point.r + 1][point.c] == point_height + 1:
        ret.append(Point2D(point.r + 1, point.c))
    if point.c > 0 and topo_map[point.r][point.c - 1] == point_height + 1:
        ret.append(Point2D(point.r, point.c - 1))
    if point.c < len(topo_map[0]) - 1 and topo_map[point.r][point.c + 1] == point_height + 1:
        ret.append(Point2D(point.r, point.c + 1))
    return ret


def analyze_trailhead(trailhead: Point2D, topo_map: list[list[int]]) -> tuple[int, Point2D]:
    to_test = get_neighbours(trailhead, topo_map)
    tops_reached = set()
    points_tested = set()
    while to_test:
        point_to_test = to_test.pop()
        if point_to_test in points_tested:
            continue
        if topo_map[point_to_test.r][point_to_test.c] == TOP_HEIGHT:
            tops_reached.add(point_to_test)
            continue
        points_tested.add(point_to_test)
        to_test.extend(get_neighbours(point_to_test, topo_map))
        if VERBOSE:
            print_map(topo_map, [point_to_test])
    return len(tops_reached), trailhead


def part1(input_file: TextIOWrapper):
    topo_map = load_input(input_file)
    trailheads = []
    for ridx, row in enumerate(topo_map):
        for cidx, cell in enumerate(row):
            if cell == 0:
                trailheads.append(Point2D(ridx, cidx))
    results = concurrent.futures.ProcessPoolExecutor(1).map(analyze_trailhead, trailheads, itertools.repeat(topo_map))
    final_result = sum(res[0] for res in results)

    print(f"Part 1: {final_result}")


def analyze_trailhead_part2(trailhead: Point2D, topo_map: list[list[int]]) -> tuple[int, Point2D]:
    to_test = collections.deque([x] for x in get_neighbours(trailhead, topo_map))
    tops_reached = set()
    while to_test:
        trail_to_test = to_test.popleft()
        point_to_test = trail_to_test[-1]
        if topo_map[point_to_test.r][point_to_test.c] == TOP_HEIGHT:
            tops_reached.add(tuple(trail_to_test))
            continue
        for next_step in get_neighbours(point_to_test, topo_map):
            to_test.append([*trail_to_test, next_step])
        if VERBOSE:
            print_map(topo_map, trail_to_test)
    return len(tops_reached), trailhead


def part2(input_file: TextIOWrapper):
    topo_map = load_input(input_file)
    trailheads = []
    for ridx, row in enumerate(topo_map):
        for cidx, cell in enumerate(row):
            if cell == 0:
                trailheads.append(Point2D(ridx, cidx))
    # results = concurrent.futures.ProcessPoolExecutor(1).map(
    #     analyze_trailhead_part2, trailheads, itertools.repeat(topo_map)
    # )
    results = [analyze_trailhead_part2(head, topo_map) for head in trailheads]
    final_result = sum(res[0] for res in results)

    print(f"Part 1: {final_result}")


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
