import gc
import time
import re
from collections import defaultdict
from itertools import combinations

from dataclasses import dataclass
from typing import NamedTuple

from tqdm.rich import tqdm

VERBOSE = 2
STARTING_VALVE = "AA"
TEST_DATA = False
if TEST_DATA:
    ...
else:
    pass


class Valve(NamedTuple):
    name: str
    flow_rate: int
    tunnels: list[tuple[str, int]]


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
                tunnels = [(tunnel, 1) for tunnel in matches["tunnels"].split(", ")]
                valves[name] = Valve(name, flow_rate, tunnels)
    return valves


def mega_tree(
    valves: dict[str, Valve],
    allowed_valves: frozenset[str],
    current_valve: str,
    opened_valves: frozenset[str],
    current_minute: int,
    time_delta: int,  # how many minutes elapsed in this iteration (current_minute - last_minute)
    pressure_released: defaultdict[str, int],
    came_from: list[str],  # a list of nodes visited since last time a valve was opened
    # for avoiding cycles between opening valves.
    all_actions: list[str],  # all actions taken, used for debugging.
    time_limit: int = 30,
) -> tuple[int, list[str]]:
    new_pressure = defaultdict(int)
    for valve in opened_valves:
        new_pressure[valve] = pressure_released[valve] + valves[valve].flow_rate * time_delta

    found_max = sum(new_pressure.values())
    best_actions = all_actions
    if current_minute >= time_limit:
        return found_max, all_actions

    if (
        current_minute
        and current_valve not in opened_valves
        and current_valve in allowed_valves  # for part2 where operates only on subset of valves
        and valves[current_valve].flow_rate > 0
    ):
        if VERBOSE > 2:
            print(f"Opening valve {current_valve} ({valves[current_valve].flow_rate})")
        new_all_actions = [*all_actions, f"{current_minute}: Open {current_valve} ({valves[current_valve].flow_rate})"]
        # we have opened the current valve so we can go back now - use a new empty came_from
        when_opened = mega_tree(
            valves,
            allowed_valves,
            current_valve,
            opened_valves | {current_valve},
            current_minute + 1,
            1,
            new_pressure,
            [],
            new_all_actions,
        )
        if when_opened[0] > found_max:
            found_max = when_opened[0]
            best_actions = when_opened[1]

    for tunnel in valves[current_valve].tunnels:
        if tunnel[0] not in came_from:
            new_came_from = [*came_from, current_valve]
            if VERBOSE > 2:
                print(f"Going from {current_valve} to {tunnel[0]} ({tunnel[1]} minute(s))")
            new_all_actions = [*all_actions, f"{current_minute}: go to {tunnel[0]} (cost {tunnel[1]})"]
            when_moved = mega_tree(
                valves,
                allowed_valves,
                tunnel[0],
                opened_valves,
                current_minute + tunnel[1],
                tunnel[1],
                new_pressure,
                new_came_from,
                new_all_actions,
            )
            if when_moved[0] > found_max:
                found_max = when_moved[0]
                best_actions = when_moved[1]

    if current_minute < time_limit:
        if VERBOSE > 2:
            print(f"Nothing to do and still have {time_limit-current_minute} minutes left")
        total_pressure_released = sum(
            pressure_released[valve] + valves[valve].flow_rate * (time_limit - current_minute + 1)
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
        valves,
        frozenset(valves),
        current_valve,
        opened_valves,
        current_minute,
        1,
        defaultdict(int, **{v: 0 for v in valves}),
        [],
        [],
    )
    print("\n".join(found_max[1]))
    print(f"part 1 max: {found_max[0]}")


def prune_broken_valves(valves: dict[str, Valve]) -> dict[str, Valve]:
    new_valves = valves.copy()

    valves_to_remove = []
    for valve in new_valves.values():
        if valve.flow_rate > 0 or valve.name == STARTING_VALVE:
            continue

        for other_end, cost in valve.tunnels:
            tunnels_to_add = [
                (candidate_tunnel[0], candidate_tunnel[1] + cost)
                for candidate_tunnel in valve.tunnels
                if candidate_tunnel[0] != other_end and candidate_tunnel[0] not in valves_to_remove
            ]
            tunnel_to_remove = None
            for other_tunnel in new_valves[other_end].tunnels:
                if other_tunnel[0] == valve.name:
                    tunnel_to_remove = other_tunnel
                    continue
                # add direct conection going through this node
                # check if the connection already exists - if so then check if the new direct one is better
                for tunnel_to_add in tunnels_to_add:
                    if other_tunnel[0] == tunnel_to_add[0] and other_tunnel[1] < tunnel_to_add[1]:
                        # the existing conection is better - skip
                        tunnels_to_add.remove(tunnel_to_add)
                        break
            assert tunnel_to_remove
            new_valves[other_end].tunnels.remove(tunnel_to_remove)
            new_valves[other_end].tunnels.extend(tunnels_to_add)

        valves_to_remove.append(valve.name)
    for valve in valves_to_remove:
        del new_valves[valve]
    if VERBOSE > 1:
        print("Reduced graph:")
        for valve in new_valves:
            print(f"{valve=}, tunnels: {new_valves[valve].tunnels}")
    return new_valves


def part_2():
    valves = load_data()
    valves = prune_broken_valves(valves)
    time_left = 26
    current_minute = 1
    opened_valves: frozenset[str] = frozenset()
    best_score = 0
    best_combination = None
    all_combinations = list(combinations(valves, len(valves) // 2))
    for combination in all_combinations:
        human_valves = frozenset(combination) | frozenset((STARTING_VALVE,))  # have to have the starting valve
        human_valves = frozenset((STARTING_VALVE, "BB", "JJ", "CC"))  # have to have the starting valve
        elephant_valves = frozenset({v for v in valves if v not in human_valves or v == STARTING_VALVE})
        print(f"Trying combination human: {human_valves}; elephant: {elephant_valves}")
        iter_start = time.perf_counter()
        human_score = mega_tree(
            valves,
            human_valves,
            STARTING_VALVE,
            opened_valves,
            current_minute,
            1,
            defaultdict(int, **{v: 0 for v in valves}),
            [],
            [],
            time_limit=time_left,
        )
        human_time = time.perf_counter() - iter_start
        print(f"Human part took: {human_time:,} seconds")
        elephant_score = mega_tree(
            valves,
            elephant_valves,
            STARTING_VALVE,
            opened_valves,
            current_minute,
            1,
            defaultdict(int, **{v: 0 for v in valves}),
            [],
            [],
            time_limit=time_left,
        )
        print(f"Total iteration time: {time.perf_counter() - iter_start} seconds")
        if VERBOSE > 0:
            print(f"Scores: Human: {human_score}, elephant: {elephant_score}")
        if (combination_score := human_score[0] + elephant_score[0]) > best_score:
            best_score = combination_score
            best_combination = human_valves, elephant_valves
            print(f"New best found: {best_score}")

    print(best_combination)
    print(f"Part 2 result: {best_score}")


if __name__ == "__main__":
    print(f"default gc: {gc.get_threshold()}")
    gc.set_threshold(167_829, 28_342, 6_893)
    part_2()
