from ast import literal_eval
from collections import defaultdict
import heapq
from functools import cmp_to_key
from itertools import zip_longest
from pprint import pprint


def load_input():
    pairs = []
    with open("input.txt") as indata:
        current_pair = []
        for line in indata:
            line = line.strip()
            if not line:
                continue
            print(f"parsing: {line}")
            parsed = literal_eval(line)
            current_pair.append(parsed)
            if len(current_pair) == 2:
                pairs.append(current_pair)
                current_pair = []
    return pairs


sentry = object()

# return -1, 0, 1
def compare_pair(left, right):
    if isinstance(left, int):
        if isinstance(right, int):
            return left - right
        else:
            return compare_pair([left], right)
    else:
        assert isinstance(left, list)
        if isinstance(right, list):
            for l_item, r_item in zip_longest(left, right, fillvalue=sentry):
                if l_item == sentry:
                    return -1
                elif r_item == sentry:
                    return 1
                ret = compare_pair(l_item, r_item)
                if ret != 0:
                    return ret
            return 0
        else:
            return compare_pair(left, [right])
    assert False, "not reached"


def part_1():
    pairs = load_input()
    pairs_in_right_order = []
    for i, pair in enumerate(pairs, 1):
        if compare_pair(*pair) < 0:
            pairs_in_right_order.append(i)
    print(sum(pairs_in_right_order))


def part_2():
    pairs = load_input()

    decoder_key_part1 = [[2]]
    decoder_key_part2 = [[6]]
    all_inputs = [decoder_key_part1, decoder_key_part2]
    for pair in pairs:
        all_inputs.extend(pair)
    all_inputs.sort(key=cmp_to_key(compare_pair))
    decoder_key1_pos = all_inputs.index(decoder_key_part1) + 1
    decoder_key2_pos = all_inputs.index(decoder_key_part2) + 1
    pprint(all_inputs)
    print(f"{decoder_key1_pos=} * {decoder_key2_pos=} = {decoder_key1_pos * decoder_key2_pos}")


if __name__ == "__main__":
    part_2()
