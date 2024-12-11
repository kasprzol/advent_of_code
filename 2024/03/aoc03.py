import argparse
import re

from rich import print


def load_input(indata) -> list[str]:
    return indata.readlines()


def part1(input_file):
    memory = load_input(input_file)
    mul_re = re.compile(r"mul\((\d{1,3}),(\d{1,3})\)")
    sum_of_muls = 0
    for memory_line in memory:
        for mul in mul_re.findall(memory_line):
            sum_of_muls += int(mul[0]) * int(mul[1])
    print(sum_of_muls)


def part2(input_file):
    memory = load_input(input_file)
    mul_re = re.compile(r"(do\(\))|(don't\(\))|(mul\((\d{1,3}),(\d{1,3})\))")
    enabled = True
    sum_of_muls = 0
    for memory_line in memory:
        for mul in mul_re.finditer(memory_line):
            match mul.group(0)[:3]:
                case "do(":
                    enabled = True
                case "don":
                    enabled = False
                case "mul" if enabled:
                    sum_of_muls += int(mul[4]) * int(mul[5])
    print(sum_of_muls)


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
