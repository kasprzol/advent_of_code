from functools import partial
from operator import itemgetter
from typing import Literal

from tqdm.rich import tqdm
from rich import print

from utils import Point


VERBOSE = 1
TEST_DATA = False

EMPTY = " "
WALL = "#"
OPEN_TILE = "."


def load_input() -> list[str]:
    with open("test_input.txt" if TEST_DATA else "input.txt") as indata:
        snafu_numbers = []
        for line in indata:
            line = line.strip()
            snafu_numbers.append(line)

    return snafu_numbers


def snafu_number_to_int(snafu: str) -> int:
    digits = {"0": 0, "1": 1, "2": 2, "-": -1, "=": -2}
    decimal = sum(digits[digit] * 5**idx for idx, digit in enumerate(reversed(snafu)))

    if VERBOSE:
        print(f"{snafu=} == {decimal}")
    return decimal


def int_to_snafu(decimal: int) -> str:
    snafu = []
    snafu_digits = {0: "0", 1: "1", 2: "2", 3: "=", 4: "-"}

    while decimal:
        digit = snafu_digits[decimal % 5]
        qqq = {0: 0, 1: 1, 2: 2, 3: -2, 4: -1}
        snafu.append(digit)
        decimal -= qqq[decimal % 5]
        decimal //= 5
    return "".join(reversed(snafu))


def test_snafu_to_decimal():
    tests = {
        1: "1",
        2: "2",
        3: "1=",
        4: "1-",
        5: "10",
        6: "11",
        7: "12",
        8: "2=",
        9: "2-",
        10: "20",
        15: "1=0",
        20: "1-0",
        2022: "1=11-2",
        12345: "1-0---0",
        314159265: "1121-1110-1=0",
        # from sample input
        1747: "1=-0-2",
        906: "12111",
        198: "2=0=",
        11: "21",
        201: "2=01",
        31: "111",
        1257: "20012",
        32: "112",
        353: "1=-1=",
        107: "1-12",
        7: "12",
        3: "1=",
        37: "122",
        # my tests:
        13: "1==",
    }
    for expected, test_input in tests.items():
        assert snafu_number_to_int(test_input) == expected
        assert int_to_snafu(expected) == test_input


test_snafu_to_decimal()


def part_1():
    snafu_numbers = load_input()
    numbers = [snafu_number_to_int(snafu) for snafu in snafu_numbers]
    sum_numbers = sum(numbers)
    print(f"{sum_numbers=} in SNAFU is {int_to_snafu(sum_numbers)}")


if __name__ == "__main__":
    part_1()
