import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence
import functools
import itertools
import tqdm
from rich import print
import difflib


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


def print_pattern(pattern):
    for row in pattern:
        out = "".join(row)
        out = out.replace("#", "[red]#[/red]")
        print(out)


def part1():
    value = 0

    patterns = read_input()

    for pattern in patterns:
        print(pattern)
        value += find_reflections(pattern)

    print(f"The value is {value}")


def diff(a: Iterable, b: Iterable):
    num_diffs = 0
    diffs = []
    for i, j in zip(a, b):
        if i != j:
            num_diffs += 1
            diffs.append("*")
        else:
            diffs.append(" ")
    return num_diffs, diffs


def verify_horizontal_reflection(pattern, row_idx, detect_smudges=False) -> bool:
    rows_above = (pattern[r] for r in range(row_idx, -1, -1))
    rows_bellow = (pattern[r] for r in range(row_idx + 1, len(pattern)))
    # rows_above = list(rows_above)
    # rows_bellow = list(rows_bellow)
    fix_was_made = False
    replacement = {"#": ".", ".": "#"}
    for rows_to_test in zip(rows_above, rows_bellow):
        if rows_to_test[0] != rows_to_test[1]:
            if not fix_was_made and detect_smudges:
                # diff = difflib.Differ()
                # differences = list(diff.compare(*rows_to_test))
                # num_diffs = len([x for x in differences if x.startswith("+")])
                num_diffs, differences = diff(*rows_to_test)
                if num_diffs == 1:
                    fix_was_made = True
                    continue
            return False
    if detect_smudges and not fix_was_made:
        print("[red]WARNING[/red]: no smudge could have been found for horizontal reflection.")
        return False
    return True


def verify_vertical_reflection(pattern, col_idx, detect_smudges=False) -> bool:
    columns_left = ([row[c] for row in pattern] for c in range(col_idx, -1, -1))
    columns_right = ([row[c] for row in pattern] for c in range(col_idx + 1, len(pattern[0])))
    # columns_left = list(columns_left)
    # columns_right = list(columns_right)
    fix_was_made = False
    for rows_to_test in zip(columns_left, columns_right):
        if rows_to_test[0] != rows_to_test[1]:
            if not fix_was_made and detect_smudges:
                # diff = difflib.Differ()
                # differences = list(diff.compare(*rows_to_test))
                # num_diffs = len([x for x in differences if x.startswith("+")])
                num_diffs, differences = diff(*rows_to_test)
                if num_diffs == 1:
                    fix_was_made = True
                    continue
            return False
    if detect_smudges and not fix_was_made:
        print("[red]WARNING[/red]: no smudge could have been found for vertical reflection.")
        return False
    return True


def find_reflections(pattern: list[list[str]]) -> int:
    row_idx = 0
    for row_a, row_b in itertools.pairwise(pattern):
        if row_a == row_b:
            if verify_horizontal_reflection(pattern, row_idx):
                return 100 * (row_idx + 1)
        row_idx += 1
    for col_a_idx, col_b_idx in itertools.pairwise(range(len(pattern[0]))):
        col_a = [x[col_a_idx] for x in pattern]
        col_b = [x[col_b_idx] for x in pattern]
        if col_a == col_b:
            if verify_vertical_reflection(pattern, col_a_idx):
                return col_a_idx + 1
    raise RuntimeError("No reflections found")


################################################################################


def find_reflections2(pattern: list[list[str]]) -> int:
    row_idx = 0
    for row_a, row_b in itertools.pairwise(pattern):
        if verify_horizontal_reflection(pattern, row_idx, detect_smudges=True):
            return 100 * (row_idx + 1)
        row_idx += 1
    for col_a_idx, col_b_idx in itertools.pairwise(range(len(pattern[0]))):
        col_a = [x[col_a_idx] for x in pattern]
        col_b = [x[col_b_idx] for x in pattern]
        if verify_vertical_reflection(pattern, col_a_idx, detect_smudges=True):
            return col_a_idx + 1
    raise RuntimeError("No reflections found")


def part2():
    value = 0

    patterns = read_input()

    for idx, pattern in enumerate(patterns, 1):
        print(idx)
        print_pattern(pattern)
        value += find_reflections2(pattern)

    print(f"The value is {value}")


if __name__ == "__main__":
    part2()
