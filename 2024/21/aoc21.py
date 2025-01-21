import argparse
import contextlib
import functools
from io import TextIOWrapper

from rich import print
from tqdm import tqdm

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
        ACTION: (">A",),
        UP: ("A",),
        DOWN: ("vA",),
        LEFT: ("v<A",),
        RIGHT: ("v>A", ">vA"),
    },
    DOWN: {
        ACTION: (">^A", "^>A"),
        UP: ("^A",),
        DOWN: (f"{ACTION}",),
        LEFT: (f"{LEFT}{ACTION}",),
        RIGHT: (f"{RIGHT}{ACTION}",),
    },
    LEFT: {
        ACTION: (">>^A",),
        UP: (">^A",),
        DOWN: (">A",),
        LEFT: ("A",),
        RIGHT: (">>A",),
    },
    RIGHT: {
        ACTION: ("^A",),
        UP: ("<^A", "^<A"),
        DOWN: ("<A",),
        LEFT: ("<<A",),
        RIGHT: ("A",),
    },
    ACTION: {
        ACTION: ("A",),
        UP: ("<A",),
        DOWN: ("<vA", "v<A"),
        LEFT: ("v<<A",),
        RIGHT: ("vA",),
    },
}

# How to move the controlled robot's arm (slave) to button FOO, while the controlling robot's (master) being on key BAR.
# The controlled robot is operating a numerical keypad.
# NUMERICAL_KEYPAD_CONTROL [BAR][FOO] = "<^>vA"
NUMERICAL_KEYPAD_CONTROL = {
    ACTION: {
        ACTION: (ACTION,),
        "0": ("<A",),
        "1": ("^<<A",),  # "<^<A"
        "2": ("^<A", "<^A"),
        "3": ("^A",),
        "4": ("^^<<A",),  # "<^<^A", "<^^<A", "^<<^A"
        "5": ("^^<A", "<^^A"),  # ^<^A
        "6": ("^^A",),
        "7": ("^^^<<A",),  # ^<^<^A,  "<^^^<A"
        "8": ("^^^<A", "<^^^A"),  # ...
        "9": ("^^^A",),
    },
    "0": {
        ACTION: (">A",),
        "0": (ACTION,),
        "1": ("^<A",),
        "2": ("^A",),
        "3": ("^>A", ">^A"),
        "4": ("^^<A",),
        "5": ("^^A",),
        "6": ("^^>A", ">^^A"),
        "7": ("^^^<A",),
        "8": ("^^^A",),
        "9": ("^^^>A", ">^^^A"),
    },
    "1": {
        ACTION: (">>vA",),
        "0": (">vA",),
        "1": (ACTION,),
        "2": (">A",),
        "3": (">>A",),
        "4": ("^A",),
        "5": ("^>A", ">^A"),
        "6": ("^>>A", ">>^A"),
        "7": ("^^A",),
        "8": ("^^>A", ">^^A"),
        "9": ("^^>>A", ">>^^A"),
    },
    "2": {
        ACTION: (">vA", "v>A"),
        "0": ("vA",),
        "1": ("<A",),
        "2": (ACTION,),
        "3": (">A",),
        "4": ("^<A", "<^A"),
        "5": ("^A",),
        "6": ("^>A", ">^A"),
        "7": ("^^<A", "<^^A"),
        "8": ("^^A",),
        "9": (">^^A", "^^>A"),
    },
    "3": {
        ACTION: ("vA",),
        "0": ("v<A", "<vA"),
        "1": ("<<A",),
        "2": ("<A",),
        "3": (ACTION,),
        "4": ("^<<A", "<<^A"),
        "5": ("^<A", "<^A"),
        "6": ("^A",),
        "7": ("^^<<A", "<<^^A"),
        "8": ("^^<A", "<^^A"),
        "9": ("^^A",),
    },
    "4": {
        ACTION: (">>vvA",),
        "0": (">vvA",),
        "1": ("vA",),
        "2": ("v>A", ">vA"),
        "3": ("v>>A", ">>vA"),
        "4": (ACTION,),
        "5": (">A",),
        "6": (">>A",),
        "7": ("^A",),
        "8": ("^>A", ">^A"),
        "9": ("^>>A", ">>^A"),
    },
    "5": {
        ACTION: (">vvA", "vv>A"),
        "0": ("vvA",),
        "1": ("<vA", "v<A"),
        "2": ("vA",),
        "3": (">vA", "v>A"),
        "4": ("<A",),
        "5": (ACTION,),
        "6": (">A",),
        "7": ("^<A", "<^A"),
        "8": ("^A",),
        "9": ("^>A", ">^A"),
    },
    "6": {
        ACTION: ("vvA",),
        "0": ("vv<A", "<vvA"),
        "1": ("<<vA", "v<<A"),
        "2": ("v<A", "<vA"),
        "3": ("vA",),
        "4": ("<<A",),
        "5": ("<A",),
        "6": ("A",),
        "7": ("^<<A", "<<^A"),
        "8": ("^<A", "<^A"),
        "9": ("^A",),
    },
    "7": {
        ACTION: (">>vvvA",),
        "0": (">vvvA",),
        "1": ("vvA",),
        "2": ("vv>A", ">vvA"),
        "3": ("vv>>A", ">>vvA"),
        "4": ("vA",),
        "5": (">vA", "v>A"),
        "6": (">>vA", "v>>A"),
        "7": ("A",),
        "8": (">A",),
        "9": (">>A",),
    },
    "8": {
        ACTION: (">vvvA", "vvv>A"),
        "0": ("vvvA",),
        "1": ("<vvA", "vv<A"),
        "2": ("vvA",),
        "3": (">vvA", "vv>A"),
        "4": ("<vA", "v<A"),
        "5": ("vA",),
        "6": (">vA", "v>A"),
        "7": ("<A",),
        "8": ("A",),
        "9": (">A",),
    },
    "9": {
        ACTION: ("vvvA",),
        "0": ("vvv<A", "<vvvA"),
        "1": ("<<vvA", "vv<<A"),
        "2": ("vv<A", "<vvA"),
        "3": ("vvA",),
        "4": ("<<vA", "v<<A"),
        "5": ("<vA", "v<A"),
        "6": ("vA",),
        "7": ("<<A",),
        "8": ("<A",),
        "9": ("A",),
    },
}


def part1_worker_helper(directional_robot_sequence: str, number_of_robots: int) -> list[str]:
    ret = [""]
    # each robot starts on ACTION
    controlled_robot_state = ACTION
    for key in directional_robot_sequence:
        intermediate_sequences = DIRECTIONAL_KEYPAD_CONTROL[controlled_robot_state][key]
        intermediate_sequence_results = []
        for intermediate_sequence in intermediate_sequences:
            if number_of_robots == 1:
                intermediate_sequence_results.append(intermediate_sequence)
            else:
                helper_result = part1_worker_helper(intermediate_sequence, number_of_robots - 1)
                intermediate_sequence_results.extend(helper_result)
        ret = [f"{r}{i}" for r in ret for i in intermediate_sequence_results]
        controlled_robot_state = key
    with contextlib.suppress(ValueError):
        ret.remove("")
    return ret


def part1_work(door_code: str, number_of_robots) -> list[str]:
    numerical_robot_state = "A"
    door_code_results = [""]
    for numerical_key in door_code:
        sequences_for_numerical_robot = NUMERICAL_KEYPAD_CONTROL[numerical_robot_state][numerical_key]
        key_results = []
        for sequence in sequences_for_numerical_robot:
            sequences_for_key = part1_worker_helper(sequence, number_of_robots)
            key_results.extend(sequences_for_key)
        numerical_robot_state = numerical_key
        door_code_results = [f"{dcr}{kr}" for dcr in door_code_results for kr in key_results]
    return door_code_results


def numeric_part(door_code: str) -> int:
    number = int("".join([i for i in door_code if i.isnumeric()]))
    return number


def part1(input_file: TextIOWrapper):
    door_codes = load_input(input_file)
    number_of_directional_robots = 2
    # number of keypads: 1 (human) directional + (number_of_directional_robots-1) directional + 1 numerical
    result = 0
    for door_code in door_codes:
        robot_moves = part1_work(door_code, number_of_directional_robots)
        moves_by_len = sorted(robot_moves, key=lambda x: len(x))
        value = numeric_part(door_code)
        complexity = value * len(moves_by_len[0])
        print(f"{door_code}: {moves_by_len[0]}\t{len(moves_by_len[0])}\t{complexity}")
        result += complexity

    print(f"Part 1: {result:,}")


@functools.cache
def part2_worker_helper(directional_robot_sequence: str, number_of_robots: int) -> int:
    ret = 0
    # each robot starts on ACTION
    controlled_robot_state = ACTION
    for key in directional_robot_sequence:
        intermediate_sequences = DIRECTIONAL_KEYPAD_CONTROL[controlled_robot_state][key]
        intermediate_sequence_length = 999999999999999999
        for intermediate_sequence in intermediate_sequences:
            if number_of_robots == 1:
                intermediate_sequence_length = min(len(intermediate_sequence), intermediate_sequence_length)
            else:
                helper_result = part2_worker_helper(intermediate_sequence, number_of_robots - 1)
                intermediate_sequence_length = min(helper_result, intermediate_sequence_length)
        ret += intermediate_sequence_length
        controlled_robot_state = key
    if number_of_robots >= 4 and VERBOSE:
        print(f"{number_of_robots=}", part2_worker_helper.cache_info())
    return ret


def part2_work(door_code: str, number_of_robots) -> int:
    numerical_robot_state = "A"
    door_code_results = 0
    for numerical_key in tqdm(door_code, desc="numerical keys"):
        sequences_for_numerical_robot = NUMERICAL_KEYPAD_CONTROL[numerical_robot_state][numerical_key]
        key_sequence_length = 999999999999999999
        for sequence in sequences_for_numerical_robot:
            sequences_for_key = part2_worker_helper(sequence, number_of_robots)
            key_sequence_length = min(sequences_for_key, key_sequence_length)
        numerical_robot_state = numerical_key
        door_code_results += key_sequence_length
    return door_code_results


def part2(input_file: TextIOWrapper):
    door_codes = load_input(input_file)
    number_of_directional_robots = 25
    # number of keypads: 1 (human) directional + (number_of_directional_robots-1) directional + 1 numerical
    result = 0
    for door_code in tqdm(door_codes, desc="door codes"):
        robot_moves_length = part2_work(door_code, number_of_directional_robots)
        value = numeric_part(door_code)
        complexity = value * robot_moves_length
        if VERBOSE:
            print(f"{door_code}: {robot_moves_length}\t{complexity}")
        result += complexity

    print(f"Part 2: {result:,}")


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
