import argparse
import itertools

from rich import print
import tqdm

VERBOSE = 1


def load_input(indata) -> list[str]:
    return indata.readlines()


def part1(input_file):
    lines = load_input(input_file)
    xmases = 0
    for line in lines:
        xmases += line.count("XMAS")
        xmases += line.count("SAMX")
    column_max = len(lines[0])
    for row in tqdm.trange(0, len(lines) - 3):
        for column in range(0, column_max):
            candidate = f"{lines[row][column]}{lines[row+1][column]}{lines[row+2][column]}{lines[row+3][column]}"
            if candidate in ("XMAS", "SAMX"):
                xmases += 1
            if column < column_max - 3:
                candidate = (
                    f"{lines[row][column]}{lines[row+1][column+1]}{lines[row+2][column+2]}{lines[row+3][column+3]}"
                )
                if candidate in ("XMAS", "SAMX"):
                    xmases += 1
            if column >= 3:
                candidate = (
                    f"{lines[row][column]}{lines[row+1][column-1]}{lines[row+2][column-2]}{lines[row+3][column-3]}"
                )
                if candidate in ("XMAS", "SAMX"):
                    xmases += 1
    print(f"Part 2: {xmases}")


def part2(input_file):
    lines = load_input(input_file)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", type=int, choices=[1, 2])
    parser.add_argument("input", type=argparse.FileType("r"), default="test_input.txt")
    arguments = parser.parse_args()
    if arguments.part == 1:
        part1(arguments.input)
    elif arguments.part == 2:
        part2(arguments.input)


if __name__ == "__main__":
    main()
