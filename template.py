import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence
import itertools
import tqdm



def part1():
    value = 0

    for line in open("input.txt").readlines():
        line = line.strip()

    print(f"The value is {value}")

################################################################################

def part2():
    value = 0

    for line in open("input.txt").readlines():
        line = line.strip()

    print(f"The value is {value}")

if __name__ == '__main__':
    part1()
