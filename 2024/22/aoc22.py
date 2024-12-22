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
from tqdm import tqdm, trange

VERBOSE = False


def load_input(indata: TextIOWrapper):
    secrets = []
    for row_idx, line in enumerate(indata):
        line = line.strip().split("#")[0]
        if not line:
            continue
        secrets.append(int(line))
    return secrets


def generate_new_secret(old: int) -> int:
    def mix(num):
        return num ^ old

    def prune(num):
        return num % 16777216  # 2 ** 24

    new = prune(mix(old * 64))
    old = new
    new = prune(mix(new // 32))
    old = new
    new = prune(mix(new * 2048))
    return new


def part1(input_file: TextIOWrapper):
    secret_numbers = load_input(input_file)
    secret_number_iterations = 2000
    result = 0
    for buyer in secret_numbers:
        initial = buyer
        for i in range(secret_number_iterations):
            buyer = generate_new_secret(buyer)
        if VERBOSE:
            print(f"{initial} -> {buyer}")
        result += buyer
    print(f"Part 1: {result:,}")


def part2(input_file: TextIOWrapper):
    secret_numbers = load_input(input_file)
    secret_number_iterations = 2000
    result = 0
    buyers_prices = []
    buyers_diffs = []
    for buyer in tqdm(secret_numbers, desc="computing buyers"):
        initial = buyer
        prices = [initial % 10]
        for _ in range(secret_number_iterations):
            buyer = generate_new_secret(buyer)
            prices.append(buyer % 10)
        buyers_prices.append(prices)
        diffs = [pair[1] - pair[0] for pair in itertools.pairwise(prices)]
        assert len(diffs) == secret_number_iterations
        buyers_diffs.append(diffs)
        prices_to_diffs = defaultdict(set)
        # we're only interested in the first occurrence of a diff
        seen_diffs = set()
        for i in range(4, secret_number_iterations + 1):
            diff = tuple(diffs[i - 4 : i])
            if diff not in seen_diffs:
                prices_to_diffs[prices[i]].add(diff)
                seen_diffs.add(diff)
        buyers_price_to_diff.append(prices_to_diffs)

    # make sure the diffs are unique (as we're looking for the 1st diff for each buyer)

    best_profit = 0
    best_diff = None
    for buyer_idx, price_to_diff in tqdm(
        enumerate(buyers_price_to_diff), desc="Finding best diff", total=len(buyers_price_to_diff)
    ):
        for price in price_to_diff:
            for diff in price_to_diff[price]:
                diff_profit = calculate_profit_for_diff(diff)
                if diff_profit > best_profit:
                    best_profit = diff_profit
                    best_diff = diff

    # 1514 -- too high
    print(f"Part 2: {best_profit=:,} for {best_diff=}")


buyers_price_to_diff = []


# TODO: sort the diff in each price and use bisect to find it
@functools.cache
def calculate_profit_for_diff(diff):
    result = 0
    for buyer in buyers_price_to_diff:
        for price in buyer:
            if diff in buyer[price]:
                result += price
                break
    return result


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
