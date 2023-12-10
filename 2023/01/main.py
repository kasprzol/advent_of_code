import re
from collections.abc import Iterable


def find_digit(line: Iterable[str]) -> str:
    for x in line:
        if x.isnumeric():
            return x


def part1():
    values = []
    sum = 0
    for line in open("input.txt"):
        left_digit = find_digit(line)
        right_digit = find_digit(reversed(line))
        value = int(f"{left_digit}{right_digit}")
        values.append(value)
        sum += value

    print(f"The value is {sum}")


def part2():
    """
     one, two, three, four, five, six, seven, eight, and nine
    :return:
    """
    r = re.compile("\\d|(one)|(two)|(three)|(four)|(five)|(six)|(seven)|(eight)|(nine)")
    str_to_num = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9
    }
    values = []
    sum = 0

    def get_int(s):
        if s in str_to_num:
            return str_to_num[s]
        return int(s)
    
    import os
    print(os.getcwd())

    for line in open("input.txt"):
        line = line.strip()
        left_digit = r.search(line)[0]
        for i in range(len(line), -1, -1):
            right_digit = r.search(line[i:])
            if right_digit:
                right_digit = right_digit[0]
                break
        value = int(f"{get_int(left_digit)}{get_int(right_digit)}")
        values.append(value)
        sum += value

    print(f"The value is {sum}")


if __name__ == '__main__':
    part2()
