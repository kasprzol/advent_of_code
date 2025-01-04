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
    register_re = re.compile(r"Register ([ABC]): (\d+)")
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
    cpu = CPU(registers, program)
    while not cpu.halted:
        cpu.clock()

    outputs = [str(i) for i in cpu.outputs]

    print(f"Part 1: {','.join(outputs)}")


def part2(input_file: TextIOWrapper):
    import multiprocessing

    registers, program = load_input(input_file)
    # decompile(program)
    last_good = [0]
    for required_output in range(1, len(program) + 1):
        good = []
        for g in last_good:
            for candidate in range(8):
                registers["A"] = g * 8 + candidate
                cpu = CPU(registers, program)
                while not cpu.halted:
                    cpu.clock()
                if cpu.outputs == program[-required_output:]:
                    good.append(g * 8 + candidate)
        last_good = good

    print(f"part 2: {sorted(last_good)}")


def decompile(program):
    def combo(i):
        match i:
            case num if 0 <= num <= 3:
                return f"{num}"
            case 4:
                return "A"
            case 5:
                return "B"
            case 6:
                return "C"
            case _:
                return "<INVALID combo parameter>"

    with open("decompile.txt", "w") as f:
        f.write(",".join([str(j) for j in program]))
        f.write("\n\n")
        for ip, (opcode, operand) in zip(range(0, 10_000_000, 2), itertools.batched(program, 2)):
            match opcode:
                case 0:
                    f.write(
                        f"{ip:3}: A = A // 2 ** {combo(operand)}\t\t; combo({operand}) ; adv ; {opcode=}; {operand=}"
                    )
                case 1:
                    f.write(f"{ip:3}: B = B ^ {operand}\t\t; bxl ; {opcode=}; {operand=}")
                case 2:
                    f.write(f"{ip:3}: B = {combo(operand)} % 8\t\t; combo({operand}) ; bst ; {opcode=}; {operand=}")
                case 3:
                    f.write(f"{ip:3}: if A != 0: goto {operand}\t\t; jnz ; {opcode=}; {operand=}")
                case 4:
                    f.write(f"{ip:3}: B = B ^ C\t\t; bxc ; {opcode=}; {operand=}")
                case 5:
                    f.write(f"{ip:3}: out({combo(operand)} % 8)\t\t; combo({operand}) ; out ; {opcode=}; {operand=}")
                case 6:
                    f.write(
                        f"{ip:3}: B = A // 2 ** {combo(operand)}\t\t; combo({operand})  ; bdv ; {opcode=}; {operand=}"
                    )
                case 7:
                    f.write(
                        f"{ip:3}: C = A // 2 ** {combo(operand)}\t\t; combo({operand})  ; cdv ; {opcode=}; {operand=}"
                    )
                case _:
                    f.write(f"{ip:3}: INVALID INSTRUCTION; {opcode=}; {operand=}")
            f.write("\n")


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
