import argparse
import functools
import itertools
from copy import deepcopy

from rich import print
import tqdm
from io import TextIOWrapper
from enum import Enum, StrEnum
import operator

VERBOSE = False


def load_input(indata: TextIOWrapper):
    equations = []
    for line in indata:
        result, parts = line.strip().split(":")
        result = int(result)
        parts = parts.split(" ")
        parts = [int(p) for p in parts if p]
        equations.append((result, parts))
    return equations


def compute(parts, operations):
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return operations[0](parts[0], parts[1])
    return compute([operations[0](parts[0], parts[1]), *parts[2:]], operations[1:])


def part1(input_file: TextIOWrapper):
    equations = load_input(input_file)
    operations = operator.add, operator.mul
    total_calibration_result = 0
    for eq in equations:
        result, parts = eq
        for candidate in itertools.product(operations, repeat=len(parts) - 1):
            possible = compute(parts, candidate)
            if VERBOSE:
                print(f"{result} =?= {parts};{candidate}")
                print(possible)
            if possible == result:
                total_calibration_result += result
                break

    print(f"part 1: {total_calibration_result}")


def concat(a, b):
    return int(f"{a}{b}")


def part2(input_file):
    equations = load_input(input_file)
    operations = operator.add, operator.mul, concat
    total_calibration_result = 0
    for eq in tqdm.tqdm(equations):
        result, parts = eq
        for candidate in itertools.product(operations, repeat=len(parts) - 1):
            possible = compute(parts, candidate)
            if VERBOSE:
                print(f"{result} =?= {parts};{candidate}")
                print(possible)
            if possible == result:
                total_calibration_result += result
                break

    print(f"part 2: {total_calibration_result}")


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
