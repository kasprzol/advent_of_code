import re
import dataclasses
import collections
import contextlib
from typing import NamedTuple
from collections.abc import Iterable, Sequence
import functools
import itertools
import tqdm
from rich import print


@dataclasses.dataclass
class Module:
    name: str
    type: str
    outputs: list = dataclasses.field(default_factory=list, repr=False)
    inputs: list = dataclasses.field(default_factory=list, init=False, repr=False)
    state: dict | str = dataclasses.field(default_factory=str, init=False)


VERBOSE = 0


def read_input() -> dict[str, Module]:
    modules: dict[str, Module] = {}
    inputs = {}
    for line in open("input.txt").readlines():
        line = line.strip()

        module, outputs = line.split(" -> ")
        if module[0] in ("%", "&"):
            module_type, module = module[0], module[1:]
        else:
            module_type = "b"
        m = Module(name=module, outputs=outputs.split(", "), type=module_type)
        for o in m.outputs:
            inputs.setdefault(o, []).append(module)
        modules[module] = m

    for target in inputs:
        for source in inputs[target]:
            # some modules that have only inputs, no outputs
            try:
                modules[target].inputs.append(source)
            except KeyError:
                modules[target] = Module(name=target, type="no-output", outputs=[])
                modules[target].inputs = [source]

    # init default state
    for m in modules.values():
        if m.type == "&":
            m.state = {i: "low" for i in m.inputs}
        elif m.type == "%":
            m.state = "off"

    return modules


def part1():
    value = 0

    iterations = 1000

    modules = read_input()

    sent_pulses = {"high": 0, "low": 0}

    for _ in range(iterations):
        events_queue = collections.deque([("broadcaster", None, "low")])
        while events_queue:
            destination, source, pulse = events_queue.popleft()
            sent_pulses[pulse] += 1

            mod = modules[destination]
            source_state = modules[source].state if source else None
            if VERBOSE >= 1:
                print(f"{source} ({source_state}) --{pulse}-> {destination} ({mod.state})")
            if mod.type == "b":  # broadcaster
                events_queue.extend([(o, destination, pulse) for o in mod.outputs])
            elif mod.type == "%":
                if pulse == "high":
                    continue
                # else:
                p = "high" if mod.state == "off" else "low"
                mod.state = "on" if mod.state == "off" else "off"
                events_queue.extend([(o, destination, p) for o in mod.outputs])
            elif mod.type == "&":
                mod.state[source] = pulse
                if all(v == "high" for v in mod.state.values()):
                    p = "low"
                else:
                    p = "high"
                events_queue.extend([(o, destination, p) for o in mod.outputs])

    print(sent_pulses)
    value = sent_pulses["high"] * sent_pulses["low"]
    print(f"The value is {value}")


################################################################################


def part2():
    value = 0

    for line in open("input.txt").readlines():
        line = line.strip()

    print(f"The value is {value}")


if __name__ == "__main__":
    part1()
