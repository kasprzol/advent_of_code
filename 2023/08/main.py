import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence
import itertools
import functools
import tqdm

from math import lcm


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

def get_route_length(starting_point, nodes, instructions):
    current_node = starting_point
    for idx, instruction in enumerate(itertools.cycle(instructions), 1):
        current_node = nodes[current_node][instruction]
        if current_node[-1] == "Z":
            return idx


def part2():
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

    instructions = [0 if i == "L" else 1 for i in instructions]
    # current_nodes = [n for n in nodes if n.endswith("A")]
    # for idx, instruction in tqdm.tqdm(enumerate(itertools.cycle(instructions), 1)):
    #     current_nodes = [nodes[n][instruction] for n in current_nodes]
    #     if all(n.endswith("Z") for n in current_nodes):
    #         break
    starting_points = [n for n in nodes if n.endswith("A")]
    print(f"Starting nodes: {starting_points}")
    route_lengths = [get_route_length(node, nodes, instructions) for node in starting_points]
    print(route_lengths)
    value = functools.reduce(lcm, route_lengths)



    print(f"The value is {value}")

if __name__ == '__main__':
    part2()
