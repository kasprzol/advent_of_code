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

    def __eq__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        if not (isinstance(other, MutablePoint) or isinstance(other, Point)):
            return NotImplemented
        return not self == other


@dataclass
class MutablePoint3d:
    x: int
    y: int
    z: int


@dataclass
class Size:
    width: int
    height: int


class Direction(enum.Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    NORTH = "UP"
    SOUTH = "DOWN"
    EAST = "RIGHT"
    WEST = "LEFT"

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


DIRECTION_REVERSE = {"UP": Direction.DOWN, "DOWN": Direction.UP, "LEFT": Direction.RIGHT, "RIGHT": Direction.LEFT}


DIRECTION_TO_VECTOR = {
    Direction.UP: Point(0, -1),
    Direction.DOWN: Point(0, 1),
    Direction.LEFT: Point(-1, 0),
    Direction.RIGHT: Point(1, 0),
}


class Edge(NamedTuple):
    target: Point3d
    weight: int


@dataclass(order=True)
class Node:
    """A graph node class for use with the Dijkstra algorithm."""

    coordinates: Point3d
    links: list[Edge] = field(default_factory=list, repr=False, init=False, compare=False)

    # def __lt__(self, other):
    #     if not isinstance(other, Node):
    #         return NotImplemented
    #     return self.coordinates < other.coordinates

    def __hash__(self) -> int:
        return hash(self.coordinates)


def dijkstra(nodes: Iterable[Node], start: Node, end_nodes: Iterable[Node]) -> dict[Point3d, Node]:
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
    parent: dict[Point3d, Node] = {start.coordinates: None}
    queue: list[tuple[int, Node]] = [(0, start)]
    for end_node in end_nodes:
        heapq.heappush(queue, (9999_9999_9999_9999, end_node))
    while queue:
        unused_dist, u = heapq.heappop(queue)
        for link in u.links:
            # TODO: support for edge weights (right now hardcoded as 1).
            if (new_distance := distance[u.coordinates] + link.weight) < distance[link.target]:
                distance[link.target] = new_distance
                parent[link.target] = u
                heapq.heappush(queue, (distance[link.target], graph[link.target]))

    return parent


# Klika – podgraf, w którym każde dwa wierzchołki są połączone krawędzią.
# Klika jest maksymalna, jeśli nie da się dodać do niej wierzchołka tak, aby razem z nią również tworzył klikę. Klika
# jest największa (najliczniejsza), jeśli nie ma w grafie kliki o większej liczbie wierzchołków.
# https://en.wikipedia.org/wiki/Clique_(graph_theory)
# https://en.wikipedia.org/wiki/Bron%E2%80%93Kerbosch_algorithm
# The recursion is initiated by setting R and X to be the empty set and P to be the vertex set of the graph.
def bron_kerbosch(r: set[str], p: set[str], x: set[str], graph: dict[str, set[str]]) -> list[set[str]]:
    """
    Bron-Kerbosch algorithm to find maximal cliques in an undirected graph.

    :param R: Current clique (set of nodes in the clique found so far).
    :param P: Candidates to extend the clique.
    :param X: Excluded nodes (nodes that should not be considered for extension).
    :param graph: The graph as a dictionary where the keys are node identifiers and the values are sets of neighboring nodes.
    """
    results = []
    if len(p) == 0 and len(x) == 0:
        return [r]
    p, orig_p = set(p), p
    x = set(x)
    for vertex in orig_p:  # don't modify while being iterated over
        v = {vertex}
        result = bron_kerbosch(r | v, p & graph[vertex], x & graph[vertex], graph=graph)
        if result:
            results.extend(result)
        p -= v
        x |= v
    return results


def find_maximal_cliques(graph):
    """
    Function to initiate Bron-Kerbosch algorithm.

    :param graph: The graph as a dictionary where the keys are node identifiers and the values are sets of neighboring nodes.
    """
    P = set(graph.keys())  # All nodes are candidates initially
    X = set()  # No nodes are excluded initially
    R = set()  # No nodes in the clique initially

    return bron_kerbosch(R, P, X, graph)


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
