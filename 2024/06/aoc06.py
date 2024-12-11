import argparse
import functools
import itertools
from concurrent.futures.process import ProcessPoolExecutor
from copy import deepcopy

from rich import print
import tqdm
from io import TextIOWrapper
from enum import Enum, StrEnum

VERBOSE = False

NEW_OBSTACLE = "@"
OBSTACLE = "#"
GUARD = "^"


class Direction(StrEnum):
    UP = "↑"
    RIGHT = "→"
    DOWN = "↓"
    LEFT = "←"


def load_input(indata: TextIOWrapper):
    lab = []
    guard_pos = None
    for idx, line in enumerate(indata):
        lab.append(list(line))
        if GUARD in line:
            guard_pos = idx, line.index(GUARD)
    assert guard_pos is not None
    return lab, guard_pos


def move_guard_forward(old_pos, direction: Direction):
    match direction:
        case Direction.UP:
            return old_pos[0] - 1, old_pos[1]
        case Direction.RIGHT:
            return old_pos[0], old_pos[1] + 1
        case Direction.DOWN:
            return old_pos[0] + 1, old_pos[1]
        case Direction.LEFT:
            return old_pos[0], old_pos[1] - 1


def rotate_right(old_direction: Direction) -> Direction:
    match old_direction:
        case Direction.UP:
            return Direction.RIGHT
        case Direction.RIGHT:
            return Direction.DOWN
        case Direction.DOWN:
            return Direction.LEFT
        case Direction.LEFT:
            return Direction.UP


def print_lab(lab, guard_pos, direction: Direction, visited_positions, new_obstacle=None):
    if new_obstacle is not None:
        lab = deepcopy(lab)
        lab[new_obstacle[0]][new_obstacle[1]] = NEW_OBSTACLE
    print("    ", end="")
    for i in range(len(lab[0])):
        print(i % 10, end="")
    print()
    for ridx, row in enumerate(lab):
        print(f"{ridx:2}: ", end="")
        for cidx, cell in enumerate(row):
            if cell == OBSTACLE:
                print(f"[white]{OBSTACLE}[/white]", end="")
                continue
            if cell == NEW_OBSTACLE:
                print(f"[yellow]{NEW_OBSTACLE}[/yellow]", end="")
                continue
            if (ridx, cidx) == guard_pos:
                print(f"[blue]{direction}[/blue]", end="")
                continue
            if (ridx, cidx) in visited_positions:
                print("[red]X[/red]", end="")
                continue
            print(".", end="")
        print("")
    print("")


def part1(input_file: TextIOWrapper):
    lab, guard_pos = load_input(input_file)
    lab_dimensions = len(lab), len(lab[0])
    direction = Direction.UP
    distinct_positions = {guard_pos}
    while True:
        if VERBOSE:
            print_lab(lab, guard_pos, direction, distinct_positions)
        # move guard forward until there's an obstacle or she walks outside
        new_pos = move_guard_forward(guard_pos, direction)
        if not (0 <= new_pos[0] < lab_dimensions[0]) or not (0 <= new_pos[1] < lab_dimensions[1]):
            # moved outside
            break
        if lab[new_pos[0]][new_pos[1]] == OBSTACLE:
            direction = rotate_right(direction)
            continue
        guard_pos = new_pos
        distinct_positions.add(new_pos)
    print(f"part 1: {len(distinct_positions)}")


def part2_worker(task) -> tuple[tuple[int, int], bool]:
    """Returns True if the guard enters a loop, False if she goes outside the lab."""
    lab, guard_pos, new_obstacle, direction, visited_positions = task
    lab_dimensions = len(lab), len(lab[0])
    print(f"Worker starting...{new_obstacle}")
    while True:
        if VERBOSE:
            print_lab(lab, guard_pos, direction, visited_positions)
        # move guard forward until there's an obstacle or she walks outside
        new_pos = move_guard_forward(guard_pos, direction)
        if not (0 <= new_pos[0] < lab_dimensions[0]) or not (0 <= new_pos[1] < lab_dimensions[1]):
            # moved outside
            return new_obstacle, False
        if lab[new_pos[0]][new_pos[1]] == OBSTACLE:
            direction = rotate_right(direction)
            continue

        guard_pos = new_pos
        if new_pos in visited_positions and direction in visited_positions[new_pos]:
            return new_obstacle, True
        visited_positions.setdefault(new_pos, []).append(direction)


def part2(input_file):
    lab, guard_pos = load_input(input_file)
    lab_dimensions = len(lab), len(lab[0])
    direction = Direction.UP
    starting_pos = guard_pos
    visited_positions = {starting_pos: [direction]}
    new_obsctacles = set()
    tasks = {}
    while True:
        if VERBOSE:
            print_lab(lab, guard_pos, direction, visited_positions)
        # move guard forward until there's an obstacle or she walks outside
        new_pos = move_guard_forward(guard_pos, direction)
        if not (0 <= new_pos[0] < lab_dimensions[0]) or not (0 <= new_pos[1] < lab_dimensions[1]):
            break
        if lab[new_pos[0]][new_pos[1]] == OBSTACLE:
            direction = rotate_right(direction)
            continue
        else:
            # simulate an obstacle and check for loops
            direction_after_rotating = rotate_right(direction)
            lab_copy = deepcopy(lab)
            lab_copy[new_pos[0]][new_pos[1]] = OBSTACLE
            if new_pos not in tasks:
                tasks[new_pos] = lab_copy, guard_pos, new_pos, direction_after_rotating, deepcopy(visited_positions)

        guard_pos = new_pos
        visited_positions.setdefault(new_pos, []).append(direction)
    # make sure we don't put an obstacle in the starting position

    with ProcessPoolExecutor() as executor:
        print("Starting workers...")
        results = executor.map(part2_worker, tasks.values())
    mnbvcxz = {}
    for answer in results:
        print(answer)
        if answer[0] in mnbvcxz:
            assert mnbvcxz[answer[0]] == answer[1]
        mnbvcxz[answer[0]] = answer[1]
    print(mnbvcxz)
    if starting_pos in mnbvcxz:
        del mnbvcxz[starting_pos]
    qqq = sum([1 for k, v in mnbvcxz.items() if v])
    print(f"part 2: {qqq}/{len(tasks)}")


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
