import gc
import heapq
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from itertools import combinations
from typing import Iterable, NamedTuple, TypeAlias

from tqdm.rich import tqdm

VERBOSE = 0
STARTING_VALVE = "AA"
TEST_DATA = False


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
    started = time.monotonic()
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
    time_took = time.monotonic() - started
    print(f"Part 1 took {time_took:.2f} seconds ({time_took/60:.2f} minutes)")
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
                # add direct connection going through this node
                # check if the connection already exists - if so then check if the new direct one is better
                for tunnel_to_add in tunnels_to_add:
                    if other_tunnel[0] == tunnel_to_add[0] and other_tunnel[1] < tunnel_to_add[1]:
                        # the existing connection is better - skip
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


@dataclass
class WorkerState:
    current_valve: str
    time: int = 1
    opened_vales: list[tuple[str, int]] = field(default_factory=set, repr=False, init=True, compare=False)
    actions: list[str] = field(default_factory=list, repr=False, init=True, compare=False)


def part2_worker(
    starting_valve: str,
    valve_distances: dict[str, dict[str, int]],
    valves: dict[str, Valve],
    allowed_valves: frozenset[str],
    time_limit: int,
):
    # we have 3 options:
    # - open the current valve
    # - move to another valve
    # - if all valves are open then just wait
    states_to_check = deque()
    states_to_check.append(WorkerState(starting_valve, 1))
    best_score = 0
    best_actions = []
    while states_to_check:
        current_state = states_to_check.popleft()

        # check if we are done
        if current_state.time >= time_limit:
            presure_released = sum(
                valves[valve[0]].flow_rate * (time_limit - valve[1]) for valve in current_state.opened_vales
            )
            if presure_released > best_score:
                best_score = presure_released
                best_actions = current_state.actions
            continue

        # open the current valve
        if (
            current_state.current_valve not in [v[0] for v in current_state.opened_vales]
            and current_state.current_valve in allowed_valves
            and valves[current_state.current_valve].flow_rate > 0
        ):
            new_state = WorkerState(
                current_state.current_valve,
                current_state.time + 1,
                [*current_state.opened_vales, (current_state.current_valve, current_state.time)],
                [*current_state.actions, f"{current_state.time}: open {current_state.current_valve}"],
            )
            states_to_check.append(new_state)

        # no point moving to another valve while we just got here - only move after we have opened a valve
        else:
            for valve in allowed_valves:
                if (
                    valve != current_state.current_valve
                    and valves[valve].flow_rate > 0
                    and valve not in [v[0] for v in current_state.opened_vales]
                ):
                    new_state = WorkerState(
                        valve,
                        current_state.time + valve_distances[current_state.current_valve][valve],
                        current_state.opened_vales,
                        [*current_state.actions, f"{current_state.time}: go to {valve}"],
                    )
                    states_to_check.append(new_state)

        # do nothing
        new_state = WorkerState(
            current_state.current_valve,
            time_limit,
            current_state.opened_vales,
            [*current_state.actions, f"{current_state.time}: wait"],
        )
        states_to_check.append(new_state)
    return best_score, best_actions


VALVE_NAME: TypeAlias = str


class Edge(NamedTuple):
    target: VALVE_NAME
    weight: int


@dataclass(order=True)
class Node:
    """A graph node class for use with the Dijkstra algorithm."""

    coordinates: VALVE_NAME
    links: list[Edge] = field(default_factory=list, repr=False, init=False, compare=False)

    # def __lt__(self, other):
    #     if not isinstance(other, Node):
    #         return NotImplemented
    #     return self.coordinates < other.coordinates

    def __hash__(self) -> int:
        return hash(self.coordinates)


def dijkstra(
    nodes: Iterable[Node], start: Node, end_nodes: Iterable[Node]
) -> tuple[dict[VALVE_NAME, Node], dict[VALVE_NAME, int]]:
    """Implementation of Dijkstra graph path finding algorithm.

    Actually finds a route from the start node to all reachable nodes.

    :param nodes: an iterable of all the nodes in the graph.
    :param start: the start node.
    :param end_nodes: an iterable of end nodes.
    :returns: a mapping of node to its parent (predecesor on the path).
    """
    graph = {node.coordinates: node for node in nodes}
    distance = defaultdict(lambda: 99_999_999)
    distance[start.coordinates] = 0
    parent: dict[VALVE_NAME, Node | None] = {start.coordinates: None}
    queue: list[tuple[int, Node]] = [(0, start)]
    for end_node in end_nodes:
        heapq.heappush(queue, (9999_9999_9999_9999, end_node))
    while queue:
        unused_dist, u = heapq.heappop(queue)
        for link in u.links:
            if (new_distance := distance[u.coordinates] + link.weight) < distance[link.target]:
                distance[link.target] = new_distance
                parent[link.target] = u
                heapq.heappush(queue, (distance[link.target], graph[link.target]))

    return parent, distance


def compute_all_paths(valves: dict[str, Valve]):
    """Find all paths from one valve to another."""
    # we need all paths to valves with flow rate > 0
    # after prune_broken_valves we can assume that all valves have flow rate > 0 (or are the starting valve)
    nodes = []
    # first build the datastructures needed for dijkstra
    for valve in valves.values():
        edges = [Edge(target=tunnel[0], weight=tunnel[1]) for tunnel in valve.tunnels]
        nodes.append(Node(coordinates=valve.name))
        nodes[-1].links = edges
    # now run dijkstra for each valve
    results = {}
    for node in nodes:
        parents, distances = dijkstra(nodes, node, nodes)
        results[node.coordinates] = dict(distances)
    return results


def part_2():
    valves = load_data()
    valves = prune_broken_valves(valves)
    valves_to_distances = compute_all_paths(valves)
    ##################
    # check with part 1
    # presure_released, actions = part2_worker(STARTING_VALVE, valves_to_distances, valves, valves.keys(), 30)
    # print(f"Part 1 result: {presure_released} ({actions})")
    # return
    ##################
    time_left = 26
    best_score = 0
    best_combination = None
    all_combinations = list(combinations(valves, len(valves) // 2))
    seen_combinations = set()
    for combination in tqdm(all_combinations):
        human_valves = frozenset(combination) | frozenset((STARTING_VALVE,))  # have to have the starting valve
        if human_valves in seen_combinations:
            continue
        elephant_valves = frozenset({v for v in valves if v not in human_valves or v == STARTING_VALVE})
        # it does not matter which one is human and which one is elephant.
        seen_combinations.add(human_valves)
        seen_combinations.add(elephant_valves)
        if VERBOSE > 0:
            print(f"Trying combination human: {human_valves}; elephant: {elephant_valves}")
        iter_start = time.perf_counter()
        human_score = part2_worker(STARTING_VALVE, valves_to_distances, valves, human_valves, time_left)
        human_time = time.perf_counter() - iter_start
        # print(f"Human part took: {human_time:,} seconds")
        elephant_score = part2_worker(STARTING_VALVE, valves_to_distances, valves, elephant_valves, time_left)
        # print(f"Total iteration time: {time.perf_counter() - iter_start} seconds")
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
