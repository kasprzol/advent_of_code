import heapq
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, NamedTuple


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        if not (isinstance(other, Point) or isinstance(other, MutablePoint)):
            return NotImplemented
        return Point(self.x + other.x, self.y + other.y)


class Point3d(NamedTuple):
    x: int
    y: int
    z: int


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


@dataclass
class MutablePoint3d:
    x: int
    y: int
    z: int


@dataclass
class Size:
    width: int
    height: int


@dataclass
class Node:
    """A graph node class for use with the Dijkstra algorithm."""

    coordinates: Point3d
    links: list[Point3d] = field(default_factory=list)

    def __lt__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        return self.coordinates < other.coordinates


def dijkstra(nodes: Iterable[Node], start: Node, end_nodes: Iterable[Node]) -> dict[Point3d, Node]:
    """Implementation of Dijkstra graph path finding algorithm.

    Actually finds a route from the start node to all reachable nodes.

    :param nodes: an iterable of all the nodes in the graph.
    :param start: the start node.
    :param end_nodes: an iterable of end nodes.
    :returns: a mapping of node to its parent (predecesor on the path.
    """
    graph = {node.coordinates: node for node in nodes}
    distance = defaultdict(lambda: 99_999_999)
    distance[start.coordinates] = 0
    parent: dict[Point3d, Node] = {start.coordinates: None}
    queue: list[tuple[int, Node]] = [(0, start)]
    for end_node in end_nodes:
        heapq.heappush(queue, (9999_9999_9999_9999, end_node))
    while queue:
        unused_dist, u = heapq.heappop(queue)
        for link in u.links:
            # TODO: support for edge weights (right now hardcoded as 1).
            if distance[link] > distance[u.coordinates] + 1:
                distance[link] = distance[u.coordinates] + 1
                parent[link] = u
                heapq.heappush(queue, (distance[link], graph[link]))

    return parent


def range_intersection(range_a: tuple[int, int], range_b: tuple[int, int]):
    """Return the result of intersection of 2 ranges of numbers.

    The ranges are interpreted as (start, length).

    Returns three values:
    - a range before the intersection (or None)
    - the intersection (or None)
    - the range after the intersection (or None)
    """
    if range_a[0] > range_b[0]:
        range_a, range_b = range_b, range_a

    range_a_start = range_a[0]
    range_b_start = range_b[0]
    range_a_end = range_a[0] + range_a[1] - 1
    range_b_end = range_b[0] + range_b[1] - 1

    def start_end_to_start_length(start: int, end: int):
        return start, end - start + 1

    intersection_start = max(range_a_start, range_b_start)
    intersection_end = min(range_a_end, range_b_end)

    if intersection_start > intersection_end:
        return range_a, None, range_b

    intersection = start_end_to_start_length(intersection_start, intersection_end)

    if range_a_start < intersection_start:
        before_start = range_a_start
        before_end = intersection_start - 1
        assert before_start <= before_end
        before = start_end_to_start_length(before_start, before_end)
    else:
        before = None

    if intersection_end < range_a_end or intersection_end < range_b_end:
        after_start = intersection_end + 1
        after_end = max(range_a_end, range_b_end)
        after = start_end_to_start_length(after_start, after_end)
    else:
        after = None

    return before, intersection, after
