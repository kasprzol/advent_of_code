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


# @functools.cache
def _get_sequence_length_helper(
    current_robot_number: int, key_to_press: str, robot_states: list[str], previous_robot_pressed_action: bool
) -> tuple[int, tuple[str, ...]]:
    """
    :param previous_robot_pressed_action: did the robot controlling this one press action?
    """

    # if it is the first controlling robot, then it just needs to make the moves on numerical keypad
    if current_robot_number == 0:
        return 0, tuple()
    input_sequence = DIRECTIONAL_KEYPAD_CONTROL[robot_states[current_robot_number]][key_to_press]
    new_state = DIRECTIONAL_STATE_TRANSITIONS[robot_states[current_robot_number]][input_sequence]
    if current_robot_number == len(robot_states) - 1:
        robot_states[current_robot_number] = new_state
        return len(input_sequence), input_sequence
    # robot controlling the robot controlling the numerical keypad - that one uses directional keypad
    else:
        if previous_robot_pressed_action:
            robot_states[current_robot_number] = new_state
        ret = 0
        output_sequence = []
        for key in input_sequence:
            result = _get_sequence_length_helper(
                current_robot_number + 1, key, robot_states, key == ACTION and previous_robot_pressed_action
            )
            ret += result[0]
            output_sequence.extend(result[1])
        return ret, tuple(output_sequence)


def get_sequence_length(key_to_press: str, robot_states: list[str]) -> int:
    """
    Returns the length of the sequence of keys to press to have the last robot press a given button (key_to_press).
    :param robot_states: List of keys each robot is pointing to (robot 0 is the one with numerical keyboard).
    """
    key_to_press_by_last_control_robot = NUMERICAL_KEYPAD_CONTROL[robot_states[0]][key_to_press]
    ret = 0
    for key in key_to_press_by_last_control_robot:
        res = _get_sequence_length_helper(1, key, robot_states, key == ACTION)
        ret += res[0]
        print(f"{key}: {res[1]}")
        robot_states[len(robot_states) - 1] = key
    return ret


# TODO: trzeba pamiętać pozycję pośrednich robotów - one idą do action tylko, jak wydają polecenie wciśnięcia, a tak
#  to cały czas są poza tym guzikiem.
def part1(input_file: TextIOWrapper):
    door_codes = load_input(input_file)
    number_of_robots = 3
    # number of keypads: 1 (human) directional + (number_of_robots-1) directional + 1 numerical
    number_of_keyboards = number_of_robots
    for door_code in door_codes:
        robot_moves = 0
        robot_states = [ACTION] * number_of_robots
        for code_char in door_code:
            robot_moves += get_sequence_length(code_char, robot_states)
            robot_states[0] = code_char
        print(f"For door code {door_code} the length of the sequence is {robot_moves}.")

    print(f"Part 1: {0:,}")


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
