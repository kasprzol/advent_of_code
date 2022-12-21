import operator
import re
from io import TextIOBase
from typing import Callable


class Human:
    def __init__(self):
        self.ops = []
        self.placeholder = object()

    def __add__(self, other):
        self.ops.append(("+", self.placeholder, other))
        return self

    def __sub__(self, other):
        self.ops.append(("-", self.placeholder, other))
        return self

    def __truediv__(self, other):
        self.ops.append(("/", self.placeholder, other))
        return self

    def __mul__(self, other):
        self.ops.append(("*", self.placeholder, other))
        return self

    def __radd__(self, other):
        self.ops.append(("+", other, self.placeholder))
        return self

    def __rsub__(self, other):
        self.ops.append(("-", other, self.placeholder))
        return self

    def __rmul__(self, other):
        self.ops.append(("*", other, self.placeholder))
        return self

    def __rtruediv__(self, other):
        self.ops.append(("/", other, self.placeholder))
        return self

    def make_equal(self, value):
        print(f"Need to make myself equal to {value}")
        helper = value
        for op in reversed(self.ops):
            if op[0] == "+":
                helper -= op[2] if op[1] == self.placeholder else op[1]
            elif op[0] == "-":
                if op[1] == self.placeholder:
                    helper += op[2]
                else:
                    helper = op[1] - helper
            elif op[0] == "*":
                helper /= op[2] if op[1] == self.placeholder else op[1]
            elif op[0] == "/":
                if op[1] == self.placeholder:
                    helper *= op[2]
                else:
                    helper = op[1] / helper
        return helper


def parse_monkey(input_filename: str) -> dict[str, dict]:
    number = re.compile(r"(?P<name>[a-zA-Z]+): (?P<number>\d+)")
    operation = re.compile(r"(?P<name>[a-zA-Z]+): (?P<sub1>[a-zA-Z]+) (?P<op>[-+/*]) (?P<sub2>[a-zA-Z]+)")
    operations = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}
    monkeys = {}
    with open(input_filename) as indata:
        for line in indata:
            line = line.strip()
            if line == "":
                continue
            if m := number.search(line):
                monkeys[m["name"]] = {"number": int(m["number"])}
            if m := operation.search(line):
                monkeys[m["name"]] = {
                    "operand1": m["sub1"],
                    "operand2": m["sub2"],
                    "op_": m["op"],
                    "op": operations[m["op"]],
                }
    return monkeys


def part1_get_monkey_value(name: str, monkeys: dict[str, dict]) -> int:
    m = monkeys[name]
    if "number" in m:
        return m["number"]
    m["number"] = m["op"](
        part1_get_monkey_value(m["operand1"], monkeys), part1_get_monkey_value(m["operand2"], monkeys)
    )
    return m["number"]


def part_1():
    monkeys = parse_monkey("input.txt")
    print(monkeys)

    print(f"the number is: {part1_get_monkey_value('root', monkeys)}")


def part2_get_monkey_value(name: str, monkeys: dict[str, dict]) -> int | Human:
    m = monkeys[name]
    if name == "humn":
        return Human()
    if "number" in m:
        return m["number"]
    m["number"] = m["op"](
        part2_get_monkey_value(m["operand1"], monkeys), part2_get_monkey_value(m["operand2"], monkeys)
    )
    return m["number"]


def part_2():
    monkeys = parse_monkey("input.txt")
    print(monkeys)

    root_left = part2_get_monkey_value(monkeys["root"]["operand1"], monkeys)
    root_right = part2_get_monkey_value(monkeys["root"]["operand2"], monkeys)

    if isinstance(root_left, Human):
        human, other = root_left, root_right
    else:
        human, other = root_right, root_left

    print(human.make_equal(other))


if __name__ == "__main__":
    part_2()
