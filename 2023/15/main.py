import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence
import functools
import itertools
import tqdm
from rich import print


def my_hash(string: str) -> int:
    cur_val = 0
    for ch in string:
        ascii_code = ord(ch)
        cur_val += ascii_code
        cur_val *= 17
        cur_val %= 256
    return cur_val


def part1():
    value = 0

    lines = []
    for line in open("input.txt").readlines():
        line = line.strip()
        lines.append(line)
    line = "".join(lines)

    for sequence in tqdm.tqdm(line.split(",")):
        value += my_hash(sequence)

    print(f"The value is {value}")


################################################################################


def part2():
    value = 0

    for line in open("input.txt").readlines():
        line = line.strip()

    print(f"The value is {value}")


if __name__ == "__main__":
    part1()
