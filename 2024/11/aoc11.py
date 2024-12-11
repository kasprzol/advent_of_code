import argparse
import collections
import itertools
from collections import deque
from io import TextIOWrapper
from typing import NamedTuple
import concurrent.futures
from rich import print
from tqdm.rich import tqdm, trange

VERBOSE = False

TOP_HEIGHT = 9


def load_input(indata: TextIOWrapper) -> list[list[int]]:
    for row_idx, line in enumerate(indata):
        line = line.split("#")[0].strip()
        if not line:
            continue
        stones = [int(i) for i in line.split(" ")]
        return stones


def blink(stones: list[int]) -> list[int]:
    new_stones = []
    for stone in stones:
        if stone == 0:
            new_stones.append(1)
        elif (l := len(number := str(stone))) % 2 == 0:
            new_stones.append(int(number[: l // 2]))
            new_stones.append(int(number[l // 2 :]))
        else:
            new_stones.append(stone * 2024)
    return new_stones


def part1(input_file: TextIOWrapper):
    stones = load_input(input_file)
    for blink_count in range(25):
        stones = blink(stones)
    final_result = len(stones)

    print(f"Part 1: {final_result}")


def blink_part2(stones: dict[int, int]) -> dict:
    new_stones = collections.defaultdict(int)
    for stone, old_count in stones.items():
        if stone == 0:
            new_stones[1] += old_count
        elif (l := len(number := str(stone))) % 2 == 0:
            new_stones[int(number[: l // 2])] += old_count
            new_stones[int(number[l // 2 :])] += old_count
        else:
            new_stones[stone * 2024] += old_count
    return new_stones


def part2(input_file: TextIOWrapper):

    stones = load_input(input_file)
    stones = {i: 1 for i in stones}
    for blink_count in trange(75):
        stones = blink_part2(stones)

    sum_of_stones = sum(stones.values())
    print(f"Part 2: {sum_of_stones}")


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
