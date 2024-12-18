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
from tqdm import tqdm, trange

VERBOSE = False


CORRUPTED = "#"
EMPTY = "."

# sample
# AREA_H = 6 + 1  # 70 + 1
# AREA_W = 6 + 1  # 70 + 1
# BYTES_FALLEN = 12  # 1024
# input
AREA_H = 70 + 1
AREA_W = 70 + 1
BYTES_FALLEN = 1024


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        if not (isinstance(other, Point) or isinstance(other, MutablePoint)):
            return NotImplemented
        return Point(self.x + other.x, self.y + other.y)


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
    bytes_fallen = 0
    for i in range(AREA_H):
        area.append([EMPTY] * AREA_W)
    for row_idx, line in enumerate(indata):
        line = line.split("#")[0].strip()
        if not line:
            continue
        x, y = line.split(",")
        x, y = int(x), int(y)
        area[y][x] = CORRUPTED
        bytes_fallen += 1
        if bytes_fallen == BYTES_FALLEN:
            break
    return area


def make_graph(area, start: Point, end: Point):
    graph: dict[Coordinate, Node] = {}

    nodes: list[Node] = []
    area_h = len(area)
    area_w = len(area[0])

    # first, create all the nodes
    for r, row in enumerate(area):
        for c, cell in enumerate(row):
            coord = Coordinate(x=c, y=r)
            blocked = cell != EMPTY
            node = Node(coord, is_blocked=blocked)
            graph[coord] = node
            nodes.append(node)

    # this will kill the GC (a graph of cycles and cycles) so disable it
    gc.collect()
    gc.disable()

    for r in range(area_h):
        for c in range(area_w):
            if area[r][c] == CORRUPTED:
                continue
            node = graph[Coordinate(x=c, y=r)]
            for direction in Direction.values():
                direction_vector = DIRECTION_TO_VECTOR[direction]
                nx = c + direction_vector[0]
                ny = r + direction_vector[1]
                if (0 <= nx < area_w) and (0 <= ny < area_h) and area[ny][nx] == EMPTY:
                    neighbour_coord = Coordinate(x=nx, y=ny)
                    if neighbour_coord in graph:
                        node.links.append(Edge(neighbour_coord, 1))
            # assert len(node.links) > 0

    # add a starting node
    start_coord = Coordinate(x=start.x, y=start.y)
    starting_node = graph[start_coord]

    end_nodes = [graph[Coordinate(x=end.x, y=end.y)]]
    return graph, nodes, starting_node, end_nodes


def part1(input_file: TextIOWrapper):
    area = load_input(input_file)
    start = Point(0, 0)
    end = Point(y=AREA_H - 1, x=AREA_W - 1)
    graph, nodes, starting_node, end_nodes = make_graph(area, start, end)
    parents, distance = dijkstra(nodes, starting_node, end_nodes=end_nodes)

    num_steps = 0
    end_node = end_nodes[0]
    node = end_node
    while parent := parents[node.coordinates]:
        num_steps += 1
        node = parent

    print(f"Part 1: {num_steps:,}")


def load_input2(indata: TextIOWrapper) -> list[Point]:
    corrupted_bytes = []
    for row_idx, line in enumerate(indata):
        line = line.split("#")[0].strip()
        if not line:
            continue
        x, y = line.split(",")
        x, y = int(x), int(y)
        corrupted_bytes.append(Point(x=x, y=y))
    return corrupted_bytes


def make_area(corrupted_bytes: Iterable[Point]):
    area = []
    for i in range(AREA_H):
        area.append([EMPTY] * AREA_W)
    for i in corrupted_bytes:
        area[i.y][i.x] = CORRUPTED
    return area


def part2(input_file: TextIOWrapper):
    corrupted_bytes = load_input2(input_file)
    start = Point(0, 0)
    end = Point(y=AREA_H - 1, x=AREA_W - 1)
    for bytes_until_no_path in trange(len(corrupted_bytes)):
        area = make_area(corrupted_bytes[: bytes_until_no_path + 1])
        graph, nodes, starting_node, end_nodes = make_graph(area, start, end)
        parents, distance = dijkstra(nodes, starting_node, end_nodes=end_nodes)

        if end_nodes[0].coordinates not in parents:
            break
        bytes_until_no_path += 1

    blocker = corrupted_bytes[bytes_until_no_path]
    print(f"Found the blocker {blocker} ({bytes_until_no_path})")

    print(f"Part 2: {blocker.x},{blocker.y}")


def _bisect_check_if_there_is_a_path(corrupted_bytes, start, end):
    area = make_area(corrupted_bytes)
    graph, nodes, starting_node, end_nodes = make_graph(area, start, end)
    parents, distance = dijkstra(nodes, starting_node, end_nodes=end_nodes)

    if end_nodes[0].coordinates not in parents:
        return False
    return True


def _bisect(corrupted_bytes, low, high, start, end):
    if low == high:
        return low
    elif low == high - 1:
        return low
    mid = low + (high - low) // 2
    if _bisect_check_if_there_is_a_path(corrupted_bytes[:mid], start, end):
        return _bisect(corrupted_bytes, mid, high, start, end)
    else:
        return _bisect(corrupted_bytes, low, mid, start, end)


def part2_bisect(input_file: TextIOWrapper):
    corrupted_bytes = load_input2(input_file)
    start = Point(0, 0)
    end = Point(y=AREA_H - 1, x=AREA_W - 1)
    bytes_until_no_path = _bisect(corrupted_bytes, 0, len(corrupted_bytes), start, end)
    blocker = corrupted_bytes[bytes_until_no_path]
    print(f"Found the blocker {blocker} ({bytes_until_no_path})")

    print(f"Part 2: {blocker.x},{blocker.y}")


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
        part2_bisect(arguments.input)


if __name__ == "__main__":
    main()
