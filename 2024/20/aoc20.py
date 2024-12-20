import argparse
import collections
import concurrent.futures
import enum
import functools
import gc
import heapq
import io
import itertools
import operator
import re
from collections import defaultdict, deque
from dataclasses import dataclass, field
from fractions import Fraction
from io import TextIOWrapper
from pathlib import Path
from typing import Iterable, NamedTuple

from rich import print
from rich.pretty import pprint
from tqdm.rich import tqdm, trange

VERBOSE = False


WALL = "#"
EMPTY = "."


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        if not (isinstance(other, Point) or isinstance(other, MutablePoint)):
            return NotImplemented
        return Point(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        return not self == other

    def distance(self, other):
        if not (isinstance(other, Point) or isinstance(other, MutablePoint)):
            raise NotImplementedError(f"Can't take distance of Point and {type(other)}")
        return abs(self.x - other.x) + abs(self.y - other.y)


@dataclass
class MutablePoint:
    x: int
    y: int

    def __add__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        return MutablePoint(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        self.x += other.x
        self.y += other.y
        return self

    def __eq__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        return not self == other

    def copy(self):
        return MutablePoint(self.x, self.y)


class Direction(enum.StrEnum):
    UP = "^"
    DOWN = "v"
    LEFT = "<"
    RIGHT = ">"

    @staticmethod
    def values():
        return (Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT)

    # a dummy method to allow comparision
    def __lt__(self, other):
        if not isinstance(other, Direction):
            return NotImplemented
        return self.value < other.value

    def reverse(self):
        return DIRECTION_REVERSE[self.value]


DIRECTION_REVERSE = {
    "UP": Direction.DOWN,
    "DOWN": Direction.UP,
    "LEFT": Direction.RIGHT,
    "RIGHT": Direction.LEFT,
    "^": Direction.DOWN,
    "v": Direction.UP,
    "<": Direction.RIGHT,
    ">": Direction.LEFT,
}

DIRECTION_TO_VECTOR = {
    Direction.UP: Point(0, -1),
    Direction.DOWN: Point(0, 1),
    Direction.LEFT: Point(-1, 0),
    Direction.RIGHT: Point(1, 0),
}


class Coordinate(NamedTuple):
    x: int
    y: int


class Edge(NamedTuple):
    target: Coordinate
    points: int

    @property
    def weight(self):
        return self.points


@dataclass(order=True)
class Node:
    """A graph node class for use with the Dijkstra algorithm."""

    coordinates: Coordinate
    links: list[Edge] = field(default_factory=list, repr=False, init=False, compare=False)
    is_blocked: bool

    # def __lt__(self, other):
    #     if not isinstance(other, Node):
    #         return NotImplemented
    #     return self.coordinates < other.coordinates

    def __hash__(self) -> int:
        return hash(self.coordinates)


def dijkstra(
    nodes: Iterable[Node], start: Node, end_nodes: Iterable[Node]
) -> tuple[dict[Coordinate, Node], dict[Coordinate, int]]:
    """Implementation of Dijkstra graph path finding algorithm.

    Actually finds a route from the start node to all reachable nodes.

    :param nodes: an iterable of all the nodes in the graph.
    :param start: the start node.
    :param end_nodes: an iterable of end nodes.
    :returns: a mapping of node to its parent (predecesor on the path).
    """
    graph = {node.coordinates: node for node in nodes}
    distance: dict[Coordinate, int] = defaultdict(lambda: 999_999_999)
    distance[start.coordinates] = 0
    parent: dict[Coordinate, Node] = {start.coordinates: None}
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


def load_input(indata: TextIOWrapper):
    area = []
    start = end = None
    for row_idx, line in enumerate(indata):
        line = line.strip()
        if not line:
            continue
        if "S" in line:
            start = Point(x=line.index("S"), y=row_idx)
            line = line.replace("S", ".")
        if "E" in line:
            end = Point(x=line.index("E"), y=row_idx)
        line = line.replace("E", ".")
        area.append(list(line))
    assert start
    assert end
    return area, start, end


def make_graph(area, start: Point, end: Point, cheat: Point | None = None):
    graph: dict[Coordinate, Node] = {}

    nodes: list[Node] = []
    area_h = len(area)
    area_w = len(area[0])

    cheat = cheat or Point(-1, -1)

    # first, create all the nodes
    for r, row in enumerate(area):
        for c, cell in enumerate(row):
            coord = Coordinate(x=c, y=r)
            blocked = cell != EMPTY
            if cheat and cheat.x == c and cheat.y == r:
                blocked = False
            node = Node(coord, is_blocked=blocked)
            graph[coord] = node
            nodes.append(node)

    # this will kill the GC (a graph of cycles and cycles) so disable it
    gc.collect()
    gc.disable()

    for r in range(area_h):
        for c in range(area_w):
            if area[r][c] == WALL and not (cheat.x == c and cheat.y == r):
                continue
            node = graph[Coordinate(x=c, y=r)]
            for direction in Direction.values():
                direction_vector = DIRECTION_TO_VECTOR[direction]
                nx = c + direction_vector[0]
                ny = r + direction_vector[1]
                if (
                    (0 <= nx < area_w)
                    and (0 <= ny < area_h)
                    and (area[ny][nx] == EMPTY or (cheat.x == nx and cheat.y == ny))
                ):
                    neighbour_coord = Coordinate(x=nx, y=ny)
                    if neighbour_coord in graph:
                        node.links.append(Edge(neighbour_coord, 1))
            # assert len(node.links) > 0

    # add a starting node
    start_coord = Coordinate(x=start.x, y=start.y)
    starting_node = graph[start_coord]

    end_nodes = [graph[Coordinate(x=end.x, y=end.y)]]
    return graph, nodes, starting_node, end_nodes


def print_cheat(area, cheat: Point):
    area_h = len(area)
    area_w = len(area[0])
    for x in range(area_w):
        print(f"{x % 10}", end="")
    print("")
    for y in range(area_h):
        print(f"{y:2}: ", end="")
        for x in range(area_w):
            p = Point(x, y)
            if p == cheat:
                print(f"[blue]![/blue]", end="")
            else:
                if area[y][x] == WALL:
                    print("[yellow]#[/yellow]", end="")
                else:
                    print("[gray].[/gray]", end="")
        print("")


def part1(input_file: TextIOWrapper):
    area, start, end = load_input(input_file)

    # first compute the normal track's time
    graph, nodes, starting_node, end_nodes = make_graph(area, start, end)
    parents, distance = dijkstra(nodes, starting_node, end_nodes=end_nodes)
    track_time = distance[end_nodes[0].coordinates]
    if VERBOSE:
        print(f"Time of track: {track_time}")

    # now go all the way from start to the finish line and remove single walls.
    # in practice, we will go from end to start as that is how the data is returned from
    # Dijkstra.
    step_coord = end_nodes[0].coordinates
    walls_removed = set()
    area_h = len(area)
    area_w = len(area[0])
    cheat_times = collections.Counter()
    progress = tqdm(desc="steps", total=track_time)
    while step_coord in parents and parents[step_coord] is not None:
        # find any single walls
        for direction in Direction.values():
            cheat1 = Point(step_coord.x, step_coord.y) + DIRECTION_TO_VECTOR[direction]
            cheat2 = cheat1 + DIRECTION_TO_VECTOR[direction]
            if not (
                0 <= cheat1.x < area_w
                and 0 <= cheat1.y < area_h
                and 0 <= cheat2.x < area_w
                and 0 <= cheat2.y < area_h
                and area[cheat1.y][cheat1.x] == WALL
                and area[cheat2.y][cheat2.x] == EMPTY
                and cheat1 not in walls_removed
            ):
                continue

            if VERBOSE:
                print_cheat(area, cheat1)
            cheat_graph, cheat_nodes, cheat_starting_node, cheat_end_nodes = make_graph(area, start, end, cheat1)
            cheat_parents, cheat_distance = dijkstra(cheat_nodes, cheat_starting_node, end_nodes=cheat_end_nodes)
            cheat_track_time = cheat_distance[cheat_end_nodes[0].coordinates]
            if cheat_track_time < track_time:
                cheat_times[track_time - cheat_track_time] += 1
            walls_removed.add(cheat1)
        progress.update(1)
        step_coord = parents[step_coord].coordinates

    num_of_cheats_above_100 = 0
    for i in sorted(cheat_times):
        print(f"there are {cheat_times[i]} cheats that save {i}")
        if i >= 100:
            num_of_cheats_above_100 += cheat_times[i]
    print(f"Part 1: {num_of_cheats_above_100:,}")


def generate_area_with_distances(distances: dict[Coordinate, int], track_time: int, area_w: int, area_h: int):
    area_with_distances = []
    for i in range(area_h):
        area_with_distances.append([-1] * area_w)
    for node, node_dist in distances.items():
        area_with_distances[node.y][node.x] = track_time - node_dist
    return area_with_distances


def part2(input_file: TextIOWrapper):
    area, start, end = load_input(input_file)

    # first compute the normal track's time
    graph, nodes, starting_node, end_nodes = make_graph(area, start, end)
    parents, distance = dijkstra(nodes, starting_node, end_nodes=end_nodes)
    track_time = distance[end_nodes[0].coordinates]
    if VERBOSE:
        print(f"Time of track: {track_time}")

    # Create a map where values are distance to end (-1 for walls). For each step on the
    # path from start to finish, check all points in distance <=20 and check what we can gain
    # by going the cheat route.
    # NOTE: include the distance of the cheat shortcut in calculations! Basically subtract
    # the distance from the current point from the path saved.
    area_h = len(area)
    area_w = len(area[0])
    area_with_distances = generate_area_with_distances(distance, track_time, area_w, area_h)

    step_coord = end_nodes[0].coordinates
    cheat_times = collections.Counter()
    progress = tqdm(desc="steps", total=track_time)
    while step_coord in parents and parents[step_coord] is not None:
        current_step_as_point = Point(step_coord.x, step_coord.y)
        step_distance_to_end = area_with_distances[current_step_as_point.y][current_step_as_point.x]
        for x in range(max(0, step_coord.x - 20, min(area_h, step_coord.x + 20 + 1))):
            for y in range(max(0, step_coord.y - 20, min(area_w, step_coord.y + 20 + 1))):
                if area_with_distances[y][x] == -1:
                    continue
                distance_to_cheat_from_step = current_step_as_point.distance(Point(x, y))
                if distance_to_cheat_from_step > 20:
                    continue
                # time saved = distance from the far point (cheat start) to the race end - distance of the current point
                # (cheat end) to the end - length of the cheat
                time_saved = area_with_distances[y][x] - step_distance_to_end - distance_to_cheat_from_step
                if time_saved > 0:
                    cheat_times[time_saved] += 1

        progress.update(1)
        step_coord = parents[step_coord].coordinates

    num_of_cheats_above_100 = 0
    for i in sorted(cheat_times):
        print(f"there are {cheat_times[i]} cheats that save {i}")
        if i >= 100:
            num_of_cheats_above_100 += cheat_times[i]
    print(f"Part 2: {num_of_cheats_above_100:,}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", type=int, choices=[1, 2])
    parser.add_argument("input", type=argparse.FileType("r"), default="test_input.txt")
    parser.add_argument("-v", "--verbose", action="store_true")
    arguments = parser.parse_args()
    global VERBOSE
    VERBOSE = arguments.verbose
    if arguments.part == 1:
        part1(arguments.input)
    elif arguments.part == 2:
        part2(arguments.input)


if __name__ == "__main__":
    main()
