import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence
from contextlib import suppress
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

    lines = []
    for line in open("input.txt").readlines():
        line = line.strip()
        lines.append(line)
    line = "".join(lines)

    label_to_hash = {}
    boxes = [{} for i in range(256)]
    for sequence in tqdm.tqdm(line.split(",")):
        if sequence[-1] == "-":
            label = sequence[:-1]
            op = "-"
            focal_length = None
        else:
            # the sequence is "<label>=<focal length>", where focal length is 1-9
            label = sequence[:-2]
            op = "="
            focal_length = int(sequence[-1])
        if label not in label_to_hash:
            label_to_hash[label] = my_hash(label)

        box_id = label_to_hash[label]
        box = boxes[box_id]
        if op == "-":
            with suppress(KeyError):
                del box[label]
        else:
            box[label] = focal_length

    for box_id, box in enumerate(boxes, 1):
        for slot, focal_length in enumerate(box.values(), 1):
            value += box_id * slot * focal_length

    print(f"The value is {value}")


if __name__ == "__main__":
    part2()
