import operator
import re
from io import TextIOBase
from typing import Callable


class Monkey:
    id_: int
    items: list[int]
    operation: Callable[[int, int], int]
    operation_arg: int
    same_arg_placeholder = object()
    test_divisible_arg: int
    if_true_target: int
    if_false_target: int

    def __repr__(self):
        return f"Monkey({self.id_}, {self.items}, /{self.test_divisible_arg}, {self.if_true_target}, {self.if_false_target})"


def parse_monkey(indata: TextIOBase) -> tuple[Monkey, bool]:
    monkey = Monkey()
    monkey_id = re.compile(r"Monkey (?P<id>\d+):")
    items = re.compile(r"Starting items: (?P<items>[\d, ]+)")
    operation = re.compile(r"Operation: new = old (?P<op>\*|\+|-) (?P<arg>\d+)")
    operation_same_arg = re.compile(r"Operation: new = old (?P<op>\*) old")
    test = re.compile(r"Test: divisible by (?P<arg>\d+)")
    if_true = re.compile(r"If true: throw to monkey (?P<arg>\d+)")
    if_false = re.compile(r"If false: throw to monkey (?P<arg>\d+)")
    operations = {
        "+": operator.add,
        "*": operator.mul,
    }
    for line in indata:
        line = line.strip()
        if line == "":
            return monkey, False
        if m := monkey_id.search(line):
            monkey.id_ = int(m["id"])
        if m := items.search(line):
            monkey.items = [int(i) for i in m["items"].split(",")]
        elif m := operation.search(line):
            monkey.operation_arg = int(m["arg"])
            monkey.operation = operations[m["op"]]
        elif m := operation_same_arg.search(line):
            monkey.operation_arg = Monkey.same_arg_placeholder
            monkey.operation = operations[m["op"]]
        elif m := test.search(line):
            monkey.test_divisible_arg = int(m["arg"])
        elif m := if_true.search(line):
            monkey.if_true_target = int(m["arg"])
        elif m := if_false.search(line):
            monkey.if_false_target = int(m["arg"])
    return monkey, True


def part_1():
    monkeys = []
    end_of_file = False
    with open("input.txt") as indata:
        while not end_of_file:
            monkey, end_of_file = parse_monkey(indata)
            monkeys.append(monkey)
    print(monkeys)
    num_of_inspections = {monkey.id_: 0 for monkey in monkeys}
    for round in range(20):
        for monkey in monkeys:
            while monkey.items:
                num_of_inspections[monkey.id_] += 1
                item = monkey.items.pop(0)
                if monkey.operation_arg == Monkey.same_arg_placeholder:
                    item = monkey.operation(item, item)
                else:
                    item = monkey.operation(item, monkey.operation_arg)
                item //= 3
                if item % monkey.test_divisible_arg == 0:
                    monkeys[monkey.if_true_target].items.append(item)
                else:
                    monkeys[monkey.if_false_target].items.append(item)
        print(f"After {round=} items:")
        for monkey in monkeys:
            print(f"{monkey.id_}: {monkey.items}")
    print(num_of_inspections)
    top2 = (sorted(num_of_inspections.values(), reverse=True))[:2]
    print(top2[0] * top2[1])


def part_2():
    monkeys = []
    end_of_file = False
    with open("input.txt") as indata:
        while not end_of_file:
            monkey, end_of_file = parse_monkey(indata)
            monkeys.append(monkey)
    print(monkeys)
    num_of_inspections = {monkey.id_: 0 for monkey in monkeys}
    divider = 1
    for monkey in monkeys:
        divider *= monkey.test_divisible_arg

    num_of_rounds = 10_000
    # num_of_rounds = 151
    for round in range(num_of_rounds):
        for monkey in monkeys:
            while monkey.items:
                num_of_inspections[monkey.id_] += 1
                item = monkey.items.pop(0)
                if monkey.operation_arg == Monkey.same_arg_placeholder:
                    item = monkey.operation(item, item)
                else:
                    item = monkey.operation(item, monkey.operation_arg)
                item = item % divider
                target = monkey.if_true_target if item % monkey.test_divisible_arg == 0 else monkey.if_false_target
                monkeys[target].items.append(item)
        if (round + 1) % 150 == 0:
            print(f"After {round=}")
            for monkey in monkeys:
                print(f"{monkey.id_}: {monkey.items}")
    print(num_of_inspections)
    top2 = (sorted(num_of_inspections.values(), reverse=True))[:2]
    print(top2[0] * top2[1])


if __name__ == '__main__':
    part_2()
