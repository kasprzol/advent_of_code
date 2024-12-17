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
from typing import Iterable, NamedTuple

from rich import print
from tqdm import tqdm, trange

VERBOSE = False


def load_input(indata: TextIOWrapper):
    program = []
    registers = {"A": 0, "B": 0, "C": 0}
    register_re = re.compile(r"Register (A|B|C): (\d+)")
    for row_idx, line in enumerate(indata):
        line = line.strip()
        if not line:
            continue
        if m := register_re.match(line):
            registers[m.group(1)] = int(m.group(2))
        elif line.startswith("Program:"):
            program = [int(opcode) for opcode in line.removeprefix("Program:").strip().split(",")]
    return registers, program


class CPU:

    def __init__(self, registers, program):
        self.a = registers["A"]
        self.b = registers["B"]
        self.c = registers["C"]
        self.program = program
        self.instruction_pointer = 0
        self.outputs = []
        self.halted = False

    def get_combo_operand_value(self, operand):
        if 0 <= operand <= 3:
            return operand
        elif operand == 4:
            return self.a
        elif operand == 5:
            return self.b
        elif operand == 6:
            return self.c
        else:
            raise RuntimeError(f"Invalid combo operand {opcode}")

    def adv(self, operand):
        numerator = self.a
        denominator = 2 ** self.get_combo_operand_value(operand)
        div = numerator / denominator
        self.a = int(div)

    def bxl(self, operand):
        self.b ^= operand

    def bst(self, operand):
        self.b = self.get_combo_operand_value(operand) % 8

    def jnz(self, operand):
        if self.a != 0:
            self.instruction_pointer = operand
            return True

    def bxc(self, operand):
        self.b ^= self.c

    def out(self, operand):
        self.outputs.append(self.get_combo_operand_value(operand) % 8)

    def bdv(self, operand):
        numerator = self.a
        denominator = 2 ** self.get_combo_operand_value(operand)
        div = numerator / denominator
        self.b = int(div)

    def cdv(self, operand):
        numerator = self.a
        denominator = 2 ** self.get_combo_operand_value(operand)
        div = numerator / denominator
        self.c = int(div)

    def perform_instruction(self, opcode, operand):
        operations = {
            0: self.adv,
            1: self.bxl,
            2: self.bst,
            3: self.jnz,
            4: self.bxc,
            5: self.out,
            6: self.bdv,
            7: self.cdv,
        }

        ret = operations[opcode](operand)
        if not ret:
            self.instruction_pointer += 2

    def clock(self):
        try:
            opcode, operand = self.program[self.instruction_pointer], self.program[self.instruction_pointer + 1]
        except IndexError:
            self.halted = True
        else:
            self.perform_instruction(opcode, operand)


def part1(input_file: TextIOWrapper):
    registers, program = load_input(input_file)
    halted = False
    cpu = CPU(registers, program)
    while not cpu.halted:
        cpu.clock()

    outputs = [str(i) for i in cpu.outputs]

    print(f"Part 1: {','.join(outputs)}")


def part2(input_file: TextIOWrapper):
    area, start, end = load_input(input_file)
    assert area
    assert start
    assert end
    graph, nodes, starting_node, end_nodes = make_graph(area, start, end)
    parents, distance = dijkstra2(nodes, starting_node, end_nodes=end_nodes)

    part2_parents.update(parents)

    min_score = 999_999_999_999_999
    min_score_end_node = end_nodes[0]
    for end_node in end_nodes:
        print(f"Parents of end node {end_node.coordinates}:")
        if end_node.coordinates not in parents:
            print(f"[red]End node {end_node} not found in parents![/red]")
            continue
        if (dist := distance[end_node.coordinates]) < min_score:
            min_score = dist
            min_score_end_node = end_node

    i = min_score_end_node
    # distinct_points = {(i.coordinates.x, i.coordinates.y)}
    # junctions_to_check = [i]
    # while junctions_to_check:
    #     i = junctions_to_check.pop()
    #     distinct_points |= {(i.coordinates.x, i.coordinates.y)}
    #     if parents[i.coordinates]:
    #         junctions_to_check.extend(parents[i.coordinates])
    distinct_points = calculare_score_helper(i)

    print(f"Part 2: {len(distinct_points):,}")


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
