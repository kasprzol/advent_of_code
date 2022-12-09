from collections import Counter
from typing import Iterable


def part_1():
    bits = []
    with open("input.txt") as indata:
        for line in indata:
            line = line.strip()
            if len(bits) != len(line):
                bits = [Counter() for _ in range(len(line))]
            for bit_num, bit_value in enumerate(line.strip()):
                bits[bit_num][bit_value] += 1
    gamma = "".join(bit.most_common()[0][0] for bit in bits)
    epsilon = "".join(bit.most_common()[1][0] for bit in bits)
    gamma = int(gamma, base=2)
    epsilon = int(epsilon, base=2)
    print(gamma * epsilon)


def part_2():
    numbers = []
    bits_count = 0
    with open("input.txt") as indata:
        for line in indata:
            line = line.strip()
            bits_count = max(bits_count, len(line))
            numbers.append(line)

    def find_rating(numbers: Iterable[str], co2: bool):
        candidates = numbers.copy()
        bit_criteria_equal = "0" if co2 else "1"
        bit_criteria_not_equal = 1 if co2 else 0
        for bit_pos in range(bits_count):
            bit = Counter()
            for number in candidates:
                bit[number[bit_pos]] += 1
            one_count, zero_count = bit["1"], bit["0"]
            bit_criteria_o2 = bit_criteria_equal if one_count == zero_count else \
            bit.most_common()[bit_criteria_not_equal][0]
            candidates = [c for c in candidates if c[bit_pos] == bit_criteria_o2]
            if len(candidates) == 1:
                break
        assert len(candidates) == 1
        return candidates[0]

    o2_rating = find_rating(numbers, False)
    co2_rating = find_rating(numbers, True)

    print(int(o2_rating, base=2) * int(co2_rating, base=2))


if __name__ == '__main__':
    part_2()
