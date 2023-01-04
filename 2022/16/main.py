import gc
import re
from collections import defaultdict

from dataclasses import dataclass
from typing import NamedTuple

from tqdm import tqdm

MAX_MINUTES = 30
VERBOSE = 0
TEST_DATA = False
if TEST_DATA:
    ...
else:
    pass


class Valve(NamedTuple):
    name: str
    flow_rate: int
    tunnels: list[str]


def load_data() -> dict[str, Valve]:
    r = re.compile(
        r"Valve (?P<valve>[A-Z]{2}) has flow rate=(?P<flow_rate>\d+); tunnels? leads? to valves? (?P<tunnels>[A-Z, ]+)"
    )
    valves = {}
    with open("input.txt") as indata:
        for line in indata:
            if matches := r.match(line):
                name = matches["valve"]
                flow_rate = int(matches["flow_rate"])
                tunnels = matches["tunnels"].split(", ")
                valves[name] = Valve(name, flow_rate, tuple(tunnels))
    return valves


def mega_tree(
    valves: dict[str, Valve],
    current_valve: str,
    opened_valves: frozenset[str],
    current_minute: int,
    pressure_released: defaultdict[str, int],
    came_from: list[str],  # a list of nodes visited since last time a valve was opened
    # for avoiding cycles between opening valves.
    all_actions: list[str],  # all actions taken, used for debugging.
) -> tuple[int, list[str]]:
    new_pressure = defaultdict(int)
    for valve in opened_valves:
        new_pressure[valve] = pressure_released[valve] + valves[valve].flow_rate

    found_max = sum(new_pressure.values())
    best_actions = all_actions
    if current_minute >= MAX_MINUTES:
        return found_max, all_actions

    if current_minute and valves[current_valve].flow_rate > 0 and current_valve not in opened_valves:
        if VERBOSE > 1:
            print(f"Opening valve {current_valve} ({valves[current_valve].flow_rate})")
        new_all_actions = [*all_actions, f"{current_minute}: Open {current_valve} ({valves[current_valve].flow_rate})"]
        # we have opened the current valve so we can go back now - use a new empty came_from
        when_opened = mega_tree(
            valves,
            current_valve,
            opened_valves | {current_valve},
            current_minute + 1,
            new_pressure,
            [],
            new_all_actions,
        )
        if when_opened[0] > found_max:
            found_max = when_opened[0]
            best_actions = when_opened[1]

    for tunnel in valves[current_valve].tunnels:
        if tunnel not in came_from:
            new_came_from = [*came_from, current_valve]
            if VERBOSE > 1:
                print(f"Going from {current_valve} to {tunnel}")
            new_all_actions = [*all_actions, f"{current_minute}: go to {tunnel}"]
            when_moved = mega_tree(
                valves, tunnel, opened_valves, current_minute + 1, new_pressure, new_came_from, new_all_actions
            )
            if when_moved[0] > found_max:
                found_max = when_moved[0]
                best_actions = when_moved[1]

    if current_minute < MAX_MINUTES:
        if VERBOSE > 1:
            print(f"Nothing to do and still have {30-current_minute} minutes left")
        total_pressure_released = sum(
            pressure_released[valve] + valves[valve].flow_rate * (MAX_MINUTES - current_minute + 1)
            for valve in opened_valves
        )
        if total_pressure_released > found_max:
            found_max = total_pressure_released
            best_actions = all_actions

    if VERBOSE > 0:
        print(found_max, best_actions)
    return found_max, best_actions


def part_1():
    valves = load_data()
    current_valve = "AA"
    time_left = 30
    current_minute = 1
    opened_valves: frozenset[str] = frozenset()
    found_max = mega_tree(
        valves, current_valve, opened_valves, current_minute, defaultdict(int, **{v: 0 for v in valves}), [], []
    )
    print("\n".join(found_max[1]))
    print(f"part 1 max: {found_max[0]}")


def part_2():
    pass


if __name__ == "__main__":
    print(f"default gc: {gc.get_threshold()}")
    gc.set_threshold(267_829, 38_342, 16_893)
    part_1()
