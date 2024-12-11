import argparse
import itertools

from rich import print

VERBOSE = 1


def load_input(indata) -> list[list[int]]:
    lists_of_numbers = []
    for line in indata:
        numbers = line.strip().split(" ")
        lists_of_numbers.append([int(number) for number in numbers if number])

    return lists_of_numbers


def is_safe(report: list[int]) -> bool:
    sign = None
    for num1, num2 in itertools.pairwise(report):
        diff = num1 - num2
        if diff not in (-3, -2, -1, 1, 2, 3):
            return False
        match diff:
            case diff if diff > 0:
                new_sign = 1
            case diff if diff < 0:
                new_sign = -1
            case _:
                new_sign = 0
        if sign is not None and new_sign != sign:
            return False
        sign = new_sign
    return True


def part1(input_file):
    lists_of_numbers = load_input(input_file)
    print(lists_of_numbers)
    number_of_safe_reports = 0
    for report in lists_of_numbers:
        if is_safe(report):
            print(f"{report=} is safe")
            number_of_safe_reports += 1
    print(number_of_safe_reports)


def part2(input_file):
    lists_of_numbers = load_input(input_file)
    print(lists_of_numbers)
    number_of_safe_reports = 0
    unsafe_reports = []
    for report in lists_of_numbers:
        if is_safe(report):
            print(f"{report=} is safe")
            number_of_safe_reports += 1
        else:
            unsafe_reports.append(report)
    for unsafe in unsafe_reports:
        for i in range(len(unsafe)):
            possibly_safe = unsafe[:i] + unsafe[i + 1 :]
            if is_safe(possibly_safe):
                number_of_safe_reports += 1
                break
    print(number_of_safe_reports)


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
