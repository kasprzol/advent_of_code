import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence
import functools
import itertools
import tqdm
from rich import print


def read_input():
    patterns = []

    current_pattern = []
    for line in open("input.txt").readlines():
        line = line.strip()
        if line:
            current_pattern.append(list(line))
        else:
            patterns.append(current_pattern)
            current_pattern = []

    patterns.append(current_pattern)
    return patterns


def part1():
    value = 0

    patterns = read_input()

    for pattern in patterns:
        print(pattern)
        value += find_reflections(pattern)

    print(f"The value is {value}")


def verify_horizontal_reflection(pattern, row_idx) -> bool:
    rows_above = (pattern[r] for r in range(row_idx, -1, -1))
    rows_bellow = (pattern[r] for r in range(row_idx + 1, len(pattern)))
    # rows_above = list(rows_above)
    # rows_bellow = list(rows_bellow)
    for rows_to_test in zip(rows_above, rows_bellow):
        if rows_to_test[0] != rows_to_test[1]:
            return False
    return True


def verify_vertical_reflection(pattern, col_idx) -> bool:
    columns_left = ([row[c] for row in pattern] for c in range(col_idx, -1, -1))
    columns_right = ([row[c] for row in pattern] for c in range(col_idx + 1, len(pattern[0])))
    # columns_left = list(columns_left)
    # columns_right = list(columns_right)
    for rows_to_test in zip(columns_left, columns_right):
        if rows_to_test[0] != rows_to_test[1]:
            return False
    return True


def find_reflections(pattern: list[list[str]]) -> int:
    reflection_type = None
    reflection_row = None
    row_idx = 0
    for row_a, row_b in itertools.pairwise(pattern):
        if row_a == row_b:
            reflection_type = "horizontal"
            reflection_row = row_a
            if verify_horizontal_reflection(pattern, row_idx):
                return 100 * (row_idx + 1)
        row_idx += 1
    for col_a_idx, col_b_idx in itertools.pairwise(range(len(pattern[0]))):
        col_a = [x[col_a_idx] for x in pattern]
        col_b = [x[col_b_idx] for x in pattern]
        if col_a == col_b:
            reflection_type = "vertical"
            reflection_col = col_a_idx
            if verify_vertical_reflection(pattern, col_a_idx):
                return col_a_idx + 1
    raise RuntimeError("No reflections found")


################################################################################


def part2():
    value = 0

    for line in open("input.txt").readlines():
        line = line.strip()

    print(f"The value is {value}")


if __name__ == "__main__":
    part1()
