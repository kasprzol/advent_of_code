import argparse
import functools
import itertools

from rich import print
import tqdm

VERBOSE = 1


def load_input(indata) -> tuple[dict[int, list[int]], dict[int, list[int]], list[list[int]]]:
    must_be_before = {}
    must_be_after = {}
    pages_to_print = []
    for line in indata.readlines():
        if "|" in line:
            before, after = line.split("|")
            before = int(before)
            after = int(after)
            must_be_after.setdefault(before, []).append(after)
            must_be_before.setdefault(after, []).append(before)
        elif "," in line:
            pages_to_print.append([int(i) for i in line.split(",")])
    return must_be_before, must_be_after, pages_to_print


def is_correct_order(must_be_before, must_be_after, pages_to_print) -> bool:
    for idx, page in enumerate(pages_to_print):
        # check that a page that is before isn't required to be after
        for actual_before_page in pages_to_print[:idx]:
            if page in must_be_after and actual_before_page in must_be_after[page]:
                return False
        # check that a page that is after isn't required to be before
        for actual_after_page in pages_to_print[idx + 1 :]:
            if page in must_be_before and actual_after_page in must_be_before[page]:
                return False
    return True


def part1(input_file):
    must_be_before, must_be_after, pages_to_print = load_input(input_file)
    sum = 0
    for pages in pages_to_print:
        if is_correct_order(must_be_before, must_be_after, pages):
            middle_page = pages[len(pages) // 2]
            sum += middle_page
    print(f"Part 1: {sum}")


def compare_for_part2(page1, page2, must_be_before):
    if page1 not in must_be_before and page2 not in must_be_before:
        return 0
    if page1 in must_be_before:
        if page2 in must_be_before[page1]:
            return 1
    if page2 in must_be_before:
        if page1 in must_be_before[page2]:
            return -1


def part2(input_file):
    must_be_before, must_be_after, pages_to_print = load_input(input_file)
    sum = 0
    incorrect = []
    for pages in pages_to_print:
        if not is_correct_order(must_be_before, must_be_after, pages):
            fixed = sorted(
                pages, key=functools.cmp_to_key(functools.partial(compare_for_part2, must_be_before=must_be_before))
            )
            print(f"fixed order from {pages} to {fixed}")
            middle_page = fixed[len(fixed) // 2]
            sum += middle_page
    print(f"Part 2: {sum}")


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
