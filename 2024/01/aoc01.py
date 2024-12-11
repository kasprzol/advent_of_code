import argparse
import collections
import operator
import sys

from rich import print

VERBOSE = 1


def load_input(indata) -> list[list[int]]:
    lists_of_numbers = []
    for line in indata:
        numbers = line.strip().split(" ")
        lists_of_numbers.append([int(number) for number in numbers if number])

    return list(zip(*lists_of_numbers))


def part1(input_file):
    lists_of_numbers = load_input(input_file)
    print(lists_of_numbers)
    sorted_lists = [sorted(l) for l in lists_of_numbers]
    print(sorted_lists)
    print(list(zip(*sorted_lists)))
    disances = [abs(operator.sub(*i)) for i in list(zip(*sorted_lists))]
    print(disances)
    print(sum(disances))


def part2(input_file):
    lists_of_numbers = load_input(input_file)
    print(lists_of_numbers)
    counts = collections.Counter(lists_of_numbers[1])
    similarity_score = 0
    for num in lists_of_numbers[0]:
        similarity_score += num * counts[num]
    print(similarity_score)


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
