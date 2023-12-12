import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence
import itertools

import tqdm
from rich import print



def extrapolate(history_data: list[int]) -> int:
    derivatives = [history_data]
    iteration = history_data
    while True:
        derivative = [b - a for a, b in itertools.pairwise(iteration)]
        derivatives.append(derivative)
        iteration = derivative
        if all(x == 0 for x in derivative):
            break
    print(derivatives)
    for d2, d1 in itertools.pairwise(reversed(derivatives)):
        d1.append(d1[-1] + d2[-1])
    return derivatives[0][-1]


def part1():
    value = 0

    for line in open("input.txt").readlines():
        line = line.strip()
        history_data = [int(x) for x in line.split()]
        value += extrapolate(history_data)

    print(f"The value is {value}")

################################################################################

def extrapolate2(history_data: list[int]) -> int:
    derivatives = [history_data]
    iteration = history_data
    while True:
        derivative = [b - a for a, b in itertools.pairwise(iteration)]
        derivatives.append(derivative)
        iteration = derivative
        if all(x == 0 for x in derivative):
            break
    print(derivatives)
    for d2, d1 in itertools.pairwise(reversed(derivatives)):
        d1.insert(0, d1[0] - d2[0])
        # print(derivatives)
    return derivatives[0][0]


def part2():
    value = 0

    for line in open("input.txt").readlines():
        line = line.strip()
        history_data = [int(x) for x in line.split()]
        value += extrapolate2(history_data)

    print(f"The value is {value}")

if __name__ == '__main__':
    part2()
