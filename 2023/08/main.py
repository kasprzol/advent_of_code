import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence
import itertools
import tqdm



def part1():
    nodes = {}
    for line in open("input.txt").readlines():
        line = line.strip()
        if not line:
            continue
        if "=" not in line:
            instructions = line
        else:
            node, children = line.split("=")
            node = node.strip()
            children = children.strip()
            nodes[node] = children.removeprefix("(").removesuffix(")").split(",")
            nodes[node] = [n.strip() for n in nodes[node]]

    current_node = "AAA"
    instructions = [0 if i == "L" else 1 for i in instructions]
    for idx, instruction in enumerate(itertools.cycle(instructions), 1):
        current_node = nodes[current_node][instruction]
        if current_node == "ZZZ":
            break


    print(f"The value is {idx}")

################################################################################

def part2():
    value = 0

    for line in open("input.txt").readlines():
        line = line.strip()

    print(f"The value is {value}")

if __name__ == '__main__':
    part1()
