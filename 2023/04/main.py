import re
from collections.abc import Iterable, Sequence




def part1():
    value = 0
    for line in open("input.txt").readlines():
        line = line.strip()
        winning_numbers, my_numbers = line.split("|")
        winning_numbers = {int(x) for x in winning_numbers.split(":")[1].split()}
        my_numbers = {int(x) for x in my_numbers.split()}

        common_numbers = my_numbers & winning_numbers
        print(f"{common_numbers=}")
        value += 2 ** (len(common_numbers)-1) if common_numbers else 0

        

    print(f"The value is {value}")


def part2():
    value = 0
    lines = open("input.txt").readlines()
    number_of_cards = {i: 1 for i in range(1, len(lines) + 1)}
    
    for card_no, line in enumerate(lines, 1):
        line = line.strip()
        winning_numbers, my_numbers = line.split("|")
        winning_numbers = {int(x) for x in winning_numbers.split(":")[1].split()}
        my_numbers = {int(x) for x in my_numbers.split()}

        common_numbers = my_numbers & winning_numbers
        print(f"{common_numbers=}")
        for i in range(card_no+1, card_no + len(common_numbers) + 1):
            number_of_cards[i] += number_of_cards[card_no]
        print(f"{number_of_cards=}")

    print(f"The value is {sum(number_of_cards.values())}")


if __name__ == '__main__':
    part2()
