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
from rich.pretty import pprint
from tqdm.rich import tqdm, trange

VERBOSE = False

UP = "^"
DOWN = "v"
LEFT = "<"
RIGHT = ">"
ACTION = "A"


def load_input(indata: TextIOWrapper):
    codes = []
    for row_idx, line in enumerate(indata):
        line = line.strip().split("#")[0]
        if not line:
            continue
        codes.append(line)
    return codes


# How to move the controlled robot's arm (slave) to button FOO, while the controlling robot's (master) being on key BAR.
# The controlled robot is operating a directional keypad.
# DIRECTIONAL_KEYPAD_CONTROL[BAR][FOO] = "<^>vA"
DIRECTIONAL_KEYPAD_CONTROL = {
    UP: {
        ACTION: (RIGHT, ACTION),
        UP: (ACTION,),
        DOWN: (DOWN, ACTION),
        LEFT: (DOWN, LEFT, ACTION),
        RIGHT: (DOWN, RIGHT, ACTION),
    },
    DOWN: {
        ACTION: (RIGHT, UP, ACTION),
        UP: (UP, ACTION),
        DOWN: (ACTION,),
        LEFT: (LEFT, ACTION),
        RIGHT: (RIGHT, ACTION),
    },
    LEFT: {
        ACTION: (RIGHT, RIGHT, UP, ACTION),
        UP: (RIGHT, UP, ACTION),
        DOWN: (RIGHT, ACTION),
        LEFT: (ACTION,),
        RIGHT: (RIGHT, RIGHT, ACTION),
    },
    RIGHT: {
        ACTION: (UP, ACTION),
        UP: (LEFT, UP, ACTION),
        DOWN: (LEFT, ACTION),
        LEFT: (LEFT, LEFT, ACTION),
        RIGHT: (ACTION,),
    },
    ACTION: {
        ACTION: (ACTION,),
        UP: (LEFT, ACTION),
        DOWN: (LEFT, DOWN, ACTION),
        LEFT: (DOWN, LEFT, LEFT, ACTION),
        RIGHT: (DOWN, ACTION),
    },
}

# How to move the controlled robot's arm (slave) to button FOO, while the controlling robot's (master) being on key BAR.
# The controlled robot is operating a numerical keypad.
# NUMERICAL_KEYPAD_CONTROL [BAR][FOO] = "<^>vA"
NUMERICAL_KEYPAD_CONTROL = {
    ACTION: {
        ACTION: (ACTION,),
        "0": (LEFT, ACTION),
        "1": (UP, LEFT, LEFT, ACTION),
        "2": (UP, LEFT, ACTION),
        "3": (UP, ACTION),
        "4": (UP, UP, LEFT, LEFT, ACTION),
        "5": (UP, UP, LEFT, ACTION),
        "6": (UP, UP, ACTION),
        "7": (UP, UP, UP, LEFT, LEFT, ACTION),
        "8": (UP, UP, UP, LEFT, ACTION),
        "9": (UP, UP, UP, ACTION),
    },
    "0": {
        ACTION: (RIGHT, ACTION),
        "0": (ACTION,),
        "1": (UP, LEFT, ACTION),
        "2": (UP, ACTION),
        "3": (UP, RIGHT, ACTION),
        "4": (UP, UP, LEFT, ACTION),
        "5": (UP, UP, ACTION),
        "6": (UP, UP, RIGHT, ACTION),
        "7": (UP, UP, UP, LEFT, ACTION),
        "8": (UP, UP, UP, ACTION),
        "9": (UP, UP, UP, RIGHT, ACTION),
    },
    "1": {
        ACTION: (RIGHT, RIGHT, DOWN, ACTION),
        "0": (RIGHT, DOWN, ACTION),
        "1": (ACTION,),
        "2": (RIGHT, ACTION),
        "3": (RIGHT, RIGHT, ACTION),
        "4": (UP, ACTION),
        "5": (UP, RIGHT, ACTION),
        "6": (UP, RIGHT, RIGHT, ACTION),
        "7": (UP, UP, ACTION),
        "8": (UP, UP, RIGHT, ACTION),
        "9": (UP, UP, RIGHT, RIGHT, ACTION),
    },
    "2": {
        ACTION: (RIGHT, DOWN, ACTION),
        "0": (DOWN, ACTION),
        "1": (
            LEFT,
            ACTION,
        ),
        "2": (ACTION,),
        "3": (RIGHT, ACTION),
        "4": (UP, LEFT, ACTION),
        "5": (UP, ACTION),
        "6": (UP, RIGHT, ACTION),
        "7": (UP, UP, LEFT, ACTION),
        "8": (UP, UP, ACTION),
        "9": (UP, UP, RIGHT, ACTION),
    },
    "3": {
        ACTION: (DOWN, ACTION),
        "0": (DOWN, LEFT, ACTION),
        "1": (LEFT, LEFT, ACTION),
        "2": (LEFT, ACTION),
        "3": (ACTION,),
        "4": (UP, LEFT, LEFT, ACTION),
        "5": (UP, LEFT, ACTION),
        "6": (UP, ACTION),
        "7": (UP, UP, LEFT, LEFT, ACTION),
        "8": (UP, UP, LEFT, ACTION),
        "9": (UP, UP, ACTION),
    },
    "4": {
        ACTION: (RIGHT, RIGHT, DOWN, DOWN, ACTION),
        "0": (RIGHT, DOWN, DOWN, ACTION),
        "1": (DOWN, ACTION),
        "2": (DOWN, RIGHT, ACTION),
        "3": (DOWN, RIGHT, RIGHT, ACTION),
        "4": (ACTION,),
        "5": (RIGHT, ACTION),
        "6": (RIGHT, RIGHT, ACTION),
        "7": (UP, ACTION),
        "8": (UP, RIGHT, ACTION),
        "9": (UP, RIGHT, RIGHT, ACTION),
    },
    "5": {
        ACTION: (RIGHT, DOWN, DOWN, ACTION),
        "0": (DOWN, DOWN, ACTION),
        "1": (DOWN, LEFT, ACTION),
        "2": (DOWN, ACTION),
        "3": (DOWN, RIGHT, ACTION),
        "4": (LEFT, ACTION),
        "5": (ACTION,),
        "6": (RIGHT, ACTION),
        "7": (UP, LEFT, ACTION),
        "8": (UP, ACTION),
        "9": (UP, RIGHT, ACTION),
    },
    "6": {
        ACTION: (DOWN, DOWN, ACTION),
        "0": (DOWN, DOWN, LEFT, ACTION),
        "1": (DOWN, LEFT, LEFT, ACTION),
        "2": (DOWN, LEFT, ACTION),
        "3": (DOWN, ACTION),
        "4": (LEFT, LEFT, ACTION),
        "5": (LEFT, ACTION),
        "6": (ACTION,),
        "7": (UP, LEFT, LEFT, ACTION),
        "8": (UP, LEFT, ACTION),
        "9": (UP, ACTION),
    },
    "7": {
        ACTION: (RIGHT, RIGHT, DOWN, DOWN, DOWN, ACTION),
        "0": (RIGHT, DOWN, DOWN, DOWN, ACTION),
        "1": (DOWN, DOWN, ACTION),
        "2": (DOWN, DOWN, RIGHT, ACTION),
        "3": (DOWN, DOWN, RIGHT, RIGHT, ACTION),
        "4": (DOWN, ACTION),
        "5": (DOWN, RIGHT, ACTION),
        "6": (DOWN, RIGHT, RIGHT, ACTION),
        "7": (ACTION,),
        "8": (RIGHT, ACTION),
        "9": (RIGHT, RIGHT, ACTION),
    },
    "8": {
        ACTION: (RIGHT, DOWN, DOWN, DOWN, ACTION),
        "0": (DOWN, DOWN, DOWN, ACTION),
        "1": (DOWN, DOWN, LEFT, ACTION),
        "2": (DOWN, DOWN, ACTION),
        "3": (DOWN, DOWN, RIGHT, ACTION),
        "4": (DOWN, LEFT, ACTION),
        "5": (DOWN, ACTION),
        "6": (DOWN, RIGHT, ACTION),
        "7": (LEFT, ACTION),
        "8": (ACTION,),
        "9": (RIGHT, ACTION),
    },
    "9": {
        ACTION: (DOWN, DOWN, DOWN, ACTION),
        "0": (DOWN, DOWN, DOWN, LEFT, ACTION),
        "1": (DOWN, DOWN, LEFT, LEFT, ACTION),
        "2": (DOWN, DOWN, LEFT, ACTION),
        "3": (DOWN, DOWN, ACTION),
        "4": (DOWN, LEFT, LEFT, ACTION),
        "5": (DOWN, LEFT, ACTION),
        "6": (DOWN, ACTION),
        "7": (LEFT, LEFT, ACTION),
        "8": (LEFT, ACTION),
        "9": (ACTION,),
    },
}

NUMERICAL_STATES_VIA_DIRECTIONAL = {
    "A": {UP: "3", LEFT: "0"},
    "0": {UP: "2", RIGHT: "A"},
    "1": {UP: "4", RIGHT: "2"},
    "2": {UP: "5", RIGHT: "3", LEFT: "1", DOWN: "0"},
    "3": {UP: "6", LEFT: "2", DOWN: "A"},
    "4": {UP: "7", RIGHT: "5", DOWN: "1"},
    "5": {UP: "8", RIGHT: "6", LEFT: "4", DOWN: "2"},
    "6": {UP: "9", LEFT: "5", DOWN: "3"},
    "7": {DOWN: "4", RIGHT: "8"},
    "8": {DOWN: "5", RIGHT: "9", LEFT: "7"},
    "9": {DOWN: "6", LEFT: "8"},
}
"""States of the numerical keypad that can be reached by directional moves."""

DIRECTIONAL_STATES_VIA_DIRECTIONAL = {
    "A": {LEFT: UP, DOWN: RIGHT},
    UP: {RIGHT: "A", DOWN: DOWN},
    LEFT: {RIGHT: DOWN},
    DOWN: {LEFT: LEFT, UP: UP, RIGHT: RIGHT},
    RIGHT: {LEFT: DOWN, UP: "A"},
}


def swap_inner_dicts(top_level: dict[str, dict[str] : tuple[str, ...]]) -> dict[str, dict[tuple[str, ...], str]]:
    ret = {}
    for inner in top_level:
        new_inner = {}
        for k, v in top_level[inner].items():
            new_inner[v] = k
        ret[inner] = new_inner
    return ret


DIRECTIONAL_STATE_TRANSITIONS = swap_inner_dicts(DIRECTIONAL_KEYPAD_CONTROL)
NUMERICAL_STATE_TRANSITIONS = swap_inner_dicts(NUMERICAL_KEYPAD_CONTROL)


def worker_helper(directional_robot_sequence: str, number_of_robots: int, controlled_robot_state: str) -> list[str]:
    ret = []
    # each robot starts on ACTION
    controlled_robot_state = ACTION
    for key in directional_robot_sequence:
        intermediate_keys = DIRECTIONAL_KEYPAD_CONTROL[controlled_robot_state][key]
        if number_of_robots == 1:
            ret.extend(intermediate_keys)
        else:
            helper_result = worker_helper(intermediate_keys, number_of_robots - 1, controlled_robot_state)
            ret.extend(helper_result)
        controlled_robot_state = key
    return ret


def part1_work(door_code: str, number_of_robots) -> list[str]:
    numerical_robot_state = "A"
    sequences = []
    for key in door_code:
        sequence_for_numerical_robot = NUMERICAL_KEYPAD_CONTROL[numerical_robot_state][key]
        sequence = worker_helper(sequence_for_numerical_robot, number_of_robots, ACTION)
        sequences.extend(sequence)
        numerical_robot_state = key
    return sequences


def numeric_part(door_code: str) -> int:
    number = int("".join([i for i in door_code if i.isnumeric()]))
    print(f"{door_code} -> {number}")
    return number


# TODO: trzeba pamiętać pozycję pośrednich robotów - one idą do action tylko, jak wydają polecenie wciśnięcia, a tak
#  to cały czas są poza tym guzikiem.
def part1(input_file: TextIOWrapper):
    door_codes = load_input(input_file)
    number_of_directional_robots = 2
    # number of keypads: 1 (human) directional + (number_of_directional_robots-1) directional + 1 numerical
    result = 0
    for door_code in door_codes:
        robot_moves = part1_work(door_code, number_of_directional_robots)
        value = numeric_part(door_code)
        complexity = value * len(robot_moves)
        print(f"{door_code}: {"".join(robot_moves)}\t{len(robot_moves)}\t{complexity}")
        result += complexity

    print(f"Part 1: {result:,}")


def part2(input_file: TextIOWrapper):
    print(f"Part 2: {0:,}")


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
