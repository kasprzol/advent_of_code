import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence
from copy import deepcopy
import functools
import itertools
import tqdm
import tqdm.rich
from rich import print


bad_spring = re.compile("#+")


def verify(springs_map, control):
    found_bad_groups = []
    for m in bad_spring.finditer("".join(springs_map)):
        found_bad_groups.append(m.end() - m.start())
    return found_bad_groups == control


def part1():
    value = 0

    condition_records = []
    for line in open("input.txt").readlines():
        line = line.strip()
        condition_records.append(line.split())

    for record in condition_records:
        springs_map = record[0]
        control = [int(i) for i in record[1].split(",")]
        posibilites = [[]]
        # replace each "?" with "." or "#" and check if it results in correct solution
        for x in springs_map:
            if x != "?":
                [a.append(x) for a in posibilites]
            else:
                new_posibilities = deepcopy(posibilites)
                [a.append(".") for a in posibilites]
                [a.append("#") for a in new_posibilities]
                posibilites.extend(new_posibilities)
        print(f"Got {len(posibilites)=} for {springs_map}")
        for posibility in posibilites:
            if verify(posibility, control):
                value += 1

    print(f"The value is {value}")


################################################################################


def part2():
    value = 0

    condition_records = []
    for line in open("input.txt").readlines():
        line = line.strip()
        condition_records.append(line.split())

    for record in condition_records:
        springs_map = f"?".join(record[0] * 5)
        control = [int(i) for i in record[1].split(",")] * 5

        posibilites = [[]]
        # replace each "?" with "." or "#" and check if it results in correct solution
        print(f"Generating posibilities for {springs_map}")
        for x in tqdm.rich.tqdm(springs_map):
            if x != "?":
                [a.append(x) for a in posibilites]
            else:
                new_posibilities = deepcopy(posibilites)
                [a.append(".") for a in posibilites]
                [a.append("#") for a in new_posibilities]
                posibilites.extend(new_posibilities)
        print(f"Got {len(posibilites)=} for {springs_map}")
        for posibility in tqdm.rich.tqdm(posibilites):
            if verify(posibility, control):
                value += 1

    print(f"The value is {value}")


if __name__ == "__main__":
    part2()
