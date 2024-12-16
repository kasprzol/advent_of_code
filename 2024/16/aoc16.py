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


WALL = "#"
EMPTY = "."
POINTS_ROTATION = 1000
POINTS_STRAIGHT = 1


# copy of 2023/17 :)


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
    direction: Direction


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
    map = []
    start = end = None
    for row_idx, line in enumerate(indata):
        line = line.strip()
        if not line:
            continue
        if "S" in line:
            col = line.index("S")
            start = Point(col, row_idx)
            line = line.replace("S", ".")
        if "E" in line:
            col = line.index("E")
            end = Point(col, row_idx)
            line = line.replace("E", ".")
        map.append(list(line))
    return map, start, end


# TODO: graph of inplace rotations (clockwise or counterclockwise 90 degrees at a time) and only moves forward
def make_graph(area, start: Point, end: Point):
    graph: dict[Coordinate, Node] = {}

    nodes: list[Node] = []
    area_h = len(area)
    area_w = len(area[0])

    # first create all the nodes
    for r, row in enumerate(area):
        for c, cell in enumerate(row):
            # for going_straight in (True, False):
            for direction in Direction.values():
                coord = Coordinate(x=c, y=r, direction=direction)
                blocked = cell != EMPTY
                node = Node(coord, is_blocked=blocked)
                graph[coord] = node
                nodes.append(node)

    # this will kill the GC (a graph of cycles and cycles) so disable it
    gc.collect()
    gc.disable()

    for r in trange(area_h, desc="rows"):
        for c in trange(area_w, desc="columns"):
            # for going_straight in (True, False):
            # direction from which we get on to this node
            if area[r][c] == WALL:
                continue
            for direction in Direction.values():
                node = graph[Coordinate(x=c, y=r, direction=direction)]
                # create straight forward link to neighbour
                direction_vector = DIRECTION_TO_VECTOR[direction]
                nx = c + direction_vector[0]
                ny = r + direction_vector[1]
                if (0 <= nx < area_w) and (0 <= ny < area_h) and area[ny][nx] == EMPTY:
                    # if nx < 0 or nx >= area_w or ny < 0 or ny >= area_h or area[ny][nx] == WALL:
                    neighbour_coord = Coordinate(x=nx, y=ny, direction=direction)
                    if neighbour_coord in graph:
                        node.links.append(Edge(neighbour_coord, POINTS_STRAIGHT))
                for rotated_direction in Direction.values():
                    # create rotation link
                    if direction != rotated_direction and rotated_direction != direction.reverse():
                        rotated_coord = Coordinate(x=c, y=r, direction=rotated_direction)
                        node.links.append(Edge(rotated_coord, POINTS_ROTATION))
                assert len(node.links) > 0

    # add a starting node
    start_coord = Coordinate(x=start.x, y=start.y, direction=Direction.RIGHT)
    starting_node = graph[start_coord]

    end_nodes = [graph[Coordinate(x=end.x, y=end.y, direction=d)] for d in Direction.values()]
    return graph, nodes, starting_node, end_nodes


def part1(input_file: TextIOWrapper):
    area, start, end = load_input(input_file)
    assert area
    assert start
    assert end
    graph, nodes, starting_node, end_nodes = make_graph(area, start, end)
    parents, distance = dijkstra(nodes, starting_node, end_nodes=end_nodes)

    min_score = 999_999_999_999_999
    for end_node in end_nodes:
        print(f"Parents of end node {end_node.coordinates}:")
        if end_node.coordinates not in parents:
            print(f"[red]End node {end_node} not found in parents![/red]")
            continue
        if (dist := distance[end_node.coordinates]) < min_score:
            min_score = dist

    print(f"Part 1: {min_score:,}")


def dijkstra2(
    nodes: Iterable[Node], start: Node, end_nodes: Iterable[Node]
) -> tuple[dict[Coordinate, list[Node]], dict[Coordinate, int]]:
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
    parent: dict[Coordinate, list[Node]] = {start.coordinates: None}
    queue: list[tuple[int, Node]] = [(0, start)]
    for end_node in end_nodes:
        heapq.heappush(queue, (9999_9999_9999_9999, end_node))
    while queue:
        unused_dist, u = heapq.heappop(queue)
        for link in u.links:
            if (new_distance := distance[u.coordinates] + link.weight) < distance[link.target]:
                distance[link.target] = new_distance
                parent[link.target] = [u]
                heapq.heappush(queue, (distance[link.target], graph[link.target]))
            elif (new_distance := distance[u.coordinates] + link.weight) == distance[link.target]:
                parent[link.target].append(u)
                heapq.heappush(queue, (distance[link.target], graph[link.target]))

    return parent, distance


part2_parents = {}


@functools.cache
def calculare_score_helper(point) -> set[Point]:
    i = point
    distinct_points = {Point(i.coordinates.x, i.coordinates.y)}
    junctions_to_check = [i]
    while junctions_to_check:
        i = junctions_to_check.pop()
        distinct_points |= {Point(i.coordinates.x, i.coordinates.y)}
        if part2_parents[i.coordinates] is None:
            continue
        for parent in part2_parents[i.coordinates]:
            distinct_points |= calculare_score_helper(parent)
    return distinct_points


def part2(input_file: TextIOWrapper):
    area, start, end = load_input(input_file)
    assert area
    assert start
    assert end
    graph, nodes, starting_node, end_nodes = make_graph(area, start, end)
    parents, distance = dijkstra2(nodes, starting_node, end_nodes=end_nodes)

    part2_parents.update(parents)

    min_score = 999_999_999_999_999
    min_score_end_node = end_nodes[0]
    for end_node in end_nodes:
        print(f"Parents of end node {end_node.coordinates}:")
        if end_node.coordinates not in parents:
            print(f"[red]End node {end_node} not found in parents![/red]")
            continue
        if (dist := distance[end_node.coordinates]) < min_score:
            min_score = dist
            min_score_end_node = end_node

    i = min_score_end_node
    # distinct_points = {(i.coordinates.x, i.coordinates.y)}
    # junctions_to_check = [i]
    # while junctions_to_check:
    #     i = junctions_to_check.pop()
    #     distinct_points |= {(i.coordinates.x, i.coordinates.y)}
    #     if parents[i.coordinates]:
    #         junctions_to_check.extend(parents[i.coordinates])
    distinct_points = calculare_score_helper(i)

    print(f"Part 2: {len(distinct_points):,}")


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
