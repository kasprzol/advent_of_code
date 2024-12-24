import argparse
import collections
import concurrent.futures
import enum
import functools
import gc
import heapq
import io
import itertools
import operator
import re
from collections import defaultdict, deque
from dataclasses import dataclass, field
from fractions import Fraction
from io import TextIOWrapper
from pathlib import Path
from typing import Iterable, NamedTuple, TypedDict

from rich import print
from rich.pretty import pprint
from tqdm import tqdm, trange

VERBOSE = False


class Gate(TypedDict):
    gate: str
    out: str
    in1: str
    in2: str
    state: bool


def load_input(indata: TextIOWrapper) -> tuple[dict, list[Gate]]:
    gates = []
    wires = {}
    init_states = {}
    gate_re = re.compile(r"(?P<in1>\w{3}) (?P<gate>[A-Z]{2,3}) (?P<in2>\w{3}) -> (?P<out>\w{3})")
    for row_idx, line in enumerate(indata):
        line = line.strip().split("#")[0]
        if not line:
            continue
        res = line.split(":")
        if len(res) == 2:
            init_states[res[0]] = bool(int(res[1]))
            wires[res[0]] = {"initial": bool(int(res[1]))}
        elif m := gate_re.match(line):
            gate = {
                "gate": m.group("gate").lower(),
                "in1": m.group("in1"),
                "in2": m.group("in2"),
                "out": m.group("out"),
            }
            gates.append(gate)
            wires.setdefault(m.group("in1"), {"name": m.group("in1")}).setdefault("destinations", []).append(gate)
            wires.setdefault(m.group("in2"), {"name": m.group("in2")}).setdefault("destinations", []).append(gate)
            wires.setdefault(m.group("out"), {})["input"] = gate
    for wire in init_states:
        wires[wire]["state"] = init_states[wire]

    return wires, gates


def part1(input_file: TextIOWrapper):
    gate_to_op = {"and": operator.and_, "or": operator.or_, "xor": operator.xor}
    wires, gates = load_input(input_file)
    all_gates_computed = False
    while not all_gates_computed:
        all_gates_computed = True
        for gate in gates:
            if "state" in gate:
                continue
            in1 = wires[gate["in1"]]
            in2 = wires[gate["in2"]]
            if "state" in in1 and "state" in in2:
                gate["state"] = gate_to_op[gate["gate"]](in1["state"], in2["state"])
                wires[gate["out"]]["state"] = gate["state"]
            all_gates_computed = False

    z = []
    for wire in sorted(wires):
        if VERBOSE and "initial" not in wires[wire]:
            print(f"{wire}: {wires[wire]['state']}")
        if wire.startswith("z"):
            z.append(wires[wire]["state"])
    result = 0
    print(z)
    for i in reversed(z):
        result <<= 1
        result += i

    print(f"Part 1: {result:,}")


def part2(input_file: TextIOWrapper):
    input_lines = load_input(input_file)
    computer_links = defaultdict(set)
    vertexes = set()
    for link in input_lines:
        side_a, side_b = link.split("-")
        vertexes.add(side_a)
        vertexes.add(side_b)
        computer_links[side_a].add(side_b)
        computer_links[side_b].add(side_a)
    all_cliques = find_maximal_cliques(computer_links)
    largest_lan = sorted(all_cliques, key=len, reverse=True)[0]

    print(f"Part 2: {','.join(sorted(largest_lan))}")


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
