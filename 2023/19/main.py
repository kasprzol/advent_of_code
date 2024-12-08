import re
import dataclasses
from typing import Any, NamedTuple
from collections.abc import Iterable, Sequence
import functools
import itertools
import operator
import tqdm
from rich import print


class Part(NamedTuple):
    x: int
    m: int
    a: int
    s: int


class Rule:
    def __init__(self, goto_target, cattegory_to_check=None, oper=None, constant=None):
        self.goto_target = goto_target
        self.cattegory_to_check = cattegory_to_check
        self.operator = oper
        self.constant = constant

    def __call__(self, part: Part) -> Any:
        if not self.cattegory_to_check:
            return self.goto_target
        value = getattr(part, self.cattegory_to_check)
        if self.operator(value, self.constant):
            return self.goto_target
        return None


def read_input():
    workflows = {}
    parts = []

    workflow_r = re.compile(r"(?P<name>\w+)\{(?P<rules>[^}]+)\}")
    part_r = re.compile(r"{x=(?P<x>\d+),m=(?P<m>\d+),a=(?P<a>\d+),s=(?P<s>\d+)}")
    reading_workflows = True
    for line in open("input.txt").readlines():
        line = line.strip()
        if line == "":
            reading_workflows = False
            continue

        if reading_workflows:
            match = workflow_r.match(line)
            assert match
            workflows[match["name"]] = match["rules"]
        else:
            match = part_r.match(line)
            parts.append(Part(int(match["x"]), int(match["m"]), int(match["a"]), int(match["s"])))

    sign_to_op = {"<": operator.lt, ">": operator.gt}

    rule_r = re.compile(r"(?P<category>[xmas])(?P<sign><|>)(?P<constant>\d+):(?P<goto_label>\w+)")
    parsed_workflows = {}
    for workflow_name in workflows:
        string_rules = workflows[workflow_name].split(",")
        parsed_rules = []
        for rule_str in string_rules:
            if match := rule_r.match(rule_str):
                rule = Rule(match["goto_label"], match["category"], sign_to_op[match["sign"]], int(match["constant"]))
            else:
                # just a goto label
                rule = Rule(rule_str)
            parsed_rules.append(rule)
        parsed_workflows[workflow_name] = parsed_rules

    return parsed_workflows, parts


def part1():
    value = 0

    workflows, parts = read_input()
    starting_workflow = "in"

    accepted = []
    rejected = []
    for part in parts:
        current_workflow = starting_workflow
        while True:
            if current_workflow == "A":
                accepted.append(part)
                break
            elif current_workflow == "R":
                rejected.append(part)
                break
            for rule in workflows[current_workflow]:
                if (result := rule(part)) is not None:
                    current_workflow = result
                    break

    for part in accepted:
        rating = part.x + part.m + part.a + part.s
        value += rating

    print(f"The value is {value}")


################################################################################


def read_input2():
    workflows = {}

    workflow_r = re.compile(r"(?P<name>\w+)\{(?P<rules>[^}]+)\}")
    for line in open("input.txt").readlines():
        line = line.strip()
        if line == "":
            break

        match = workflow_r.match(line)
        assert match
        workflows[match["name"]] = match["rules"]

    rule_r = re.compile(r"(?P<category>[xmas])(?P<sign><|>)(?P<constant>\d+):(?P<goto_label>\w+)")
    parsed_workflows = {}
    for workflow_name in workflows:
        string_rules = workflows[workflow_name].split(",")
        parsed_rules = []
        for rule_str in string_rules:
            if match := rule_r.match(rule_str):
                rule = match["category"], match["sign"], int(match["constant"]), match["goto_label"]
            else:
                # just a goto label
                rule = (rule_str,)
            parsed_rules.append(rule)
        parsed_workflows[workflow_name] = parsed_rules

    return parsed_workflows


def part2():
    value = 0

    workflows = read_input2()
    all_branches_expanded = False
    space = {}
    starting_workflow = "in"
    current_workflow = starting_workflow
    for workflow in workflows:
        subtree = {}
        for rule in workflows[workflow]:
            if len(rule) == 1:
                # subtree = rule
                subtree[""] = rule[0]
            else:
                subtree[(rule[0], rule[1], rule[2])] = rule[3]
        space[workflow] = subtree

    while not all_branches_expanded:
        break
    # go throuht the tree. have a data structure to represent a set of ranges of accepted values,
    # starting with (1,4000). At each
    # tree branch make a copy of it and adjust the ranges. recurse until "A" or "R"

    print(f"The value is {value}")


if __name__ == "__main__":
    part2()
