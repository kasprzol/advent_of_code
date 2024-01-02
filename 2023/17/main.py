import dataclasses
import enum
import functools
import gc
import heapq
import itertools
import re
from collections import defaultdict
from collections.abc import Iterable, Sequence
from typing import Any, NamedTuple

import tqdm
from rich import print


class Direction(enum.Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

    @staticmethod
    def values() -> Any:
        return (Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT)

    # a dummy method to allow comparision
    def __lt__(self, other):
        if not isinstance(other, Direction):
            return NotImplemented
        return self.value < other.value

    def reverse(self):
        return DIRECTION_REVERSE[self.value]


DIRECTION_REVERSE = {"UP": Direction.DOWN, "DOWN": Direction.UP, "LEFT": Direction.RIGHT, "RIGHT": Direction.LEFT}


DIRECTION_TO_VECTOR = {Direction.UP: (0, -1), Direction.DOWN: (0, 1), Direction.LEFT: (-1, 0), Direction.RIGHT: (1, 0)}


# copied from utils
class Coordinate(NamedTuple):
    x: int
    y: int
    step_num: int
    direction: Direction


class Edge(NamedTuple):
    target: Coordinate
    weight: int


@dataclasses.dataclass(order=True)
class Node:
    """A graph node class for use with the Dijkstra algorithm."""

    coordinates: Coordinate
    heat_lost: int
    links: list[Edge] = dataclasses.field(default_factory=list, init=False, compare=False, repr=False)

    # def __lt__(self, other):
    #     if not isinstance(other, Node):
    #         return NotImplemented
    #     return self.coordinates < other.coordinates

    def __hash__(self) -> int:
        return hash((self.coordinates, self.heat_lost))


def dijkstra(nodes: Iterable[Node], start: Node, end_nodes: Iterable[Node]) -> dict[Coordinate, Node]:
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
    parent: dict[Coordinate, Node] = {start.coordinates: None}
    queue: list[tuple[int, Node]] = [(0, start)]
    for end_node in end_nodes:
        heapq.heappush(queue, (9999_9999_9999_9999, end_node))
    while queue:
        unused_dist, u = heapq.heappop(queue)
        for link in u.links:
            if distance[link.target] > (new_distance := distance[u.coordinates] + link.weight):
                distance[link.target] = new_distance
                parent[link.target] = u
                heapq.heappush(queue, (distance[link], graph[link.target]))

    return parent


def generate_graph(max_steps_in_one_direction=3):
    area = []
    for line in open("input.txt").readlines():
        line = line.strip()
        area.append([int(i) for i in line])

    # have to store 4 pieces of information for each node:
    # it's coordinates
    # from which direction we're entering this node
    # how many steps in this direction were already taken

    graph: dict[Coordinate, Node] = {}

    nodes: list[Node] = []
    area_h = len(area)
    area_w = len(area[0])

    # first create all the nodes
    for r, row in enumerate(area):
        for c, cell in enumerate(row):
            for num_steps in range(1, max_steps_in_one_direction + 1):
                for direction in Direction.values():
                    coord = Coordinate(x=c, y=r, step_num=num_steps, direction=direction)
                    node = Node(coord, heat_lost=cell)
                    graph[coord] = node
                    nodes.append(node)

    # this will kill the GC (a graph of cycles and cycles) so disable it
    gc.collect()
    gc.disable()

    for r in tqdm.trange(area_h, desc="rows"):
        for c in tqdm.trange(area_w, desc="columns"):
            for num_steps in tqdm.trange(1, max_steps_in_one_direction + 1, desc="steps"):
                # direction from which we get on to this node
                for direction in Direction.values():
                    node = graph[Coordinate(x=c, y=r, direction=direction, step_num=num_steps)]
                    for neighbour_direction in Direction.values():
                        # create links to neighbours
                        # "Because it is difficult to keep the top-heavy crucible going in a straight line for
                        # very long, it can move at most three blocks in a single direction before it must turn
                        # 90 degrees left or right. The crucible also can't reverse direction; after entering
                        # each city block, it may only turn left, continue straight, or turn right."
                        direction_vector = DIRECTION_TO_VECTOR[neighbour_direction]
                        nx = c + direction_vector[0]
                        ny = r + direction_vector[1]
                        if nx < 0 or nx >= area_w or ny < 0 or ny >= area_h:
                            continue
                        # can't go any further in that direction
                        if direction == neighbour_direction:
                            if num_steps == max_steps_in_one_direction:
                                continue
                            else:
                                neighbour = graph[
                                    Coordinate(nx, ny, step_num=num_steps + 1, direction=neighbour_direction)
                                ]
                        else:
                            # 1st step in new direction
                            if neighbour_direction == direction.reverse():
                                continue
                            neighbour = graph[Coordinate(nx, ny, direction=neighbour_direction, step_num=1)]
                        node.links.append(Edge(neighbour.coordinates, neighbour.heat_lost))

    # add a starting node
    starting_node = Node(Coordinate(0, 0, direction=Direction.DOWN, step_num=0), heat_lost=0)
    starting_node.links.append(
        Edge(
            Coordinate(x=1, y=0, direction=Direction.RIGHT, step_num=1),
            graph[Coordinate(x=1, y=0, direction=Direction.RIGHT, step_num=1)].heat_lost,
        )
    )
    starting_node.links.append(
        Edge(
            Coordinate(x=0, y=1, direction=Direction.DOWN, step_num=1),
            graph[Coordinate(x=0, y=1, direction=Direction.DOWN, step_num=1)].heat_lost,
        )
    )
    nodes.append(starting_node)
    graph[Coordinate(x=0, y=0, step_num=0, direction=Direction.DOWN)] = starting_node

    end_nodes = [
        graph[Coordinate(x=area_w - 1, y=area_h - 1, step_num=s, direction=d)]
        for d in Direction.values()
        for s in range(1, max_steps_in_one_direction + 1)
    ]
    return graph, nodes, starting_node, end_nodes


def part1():
    value = 2**50

    graph, nodes, starting_node, end_nodes = generate_graph()
    parents = dijkstra(nodes, starting_node, end_nodes=end_nodes)

    for end_node in end_nodes:
        print(f"Parents of end node {end_node.coordinates}:")
        if end_node.coordinates not in parents:
            print(f"[red]End node {end_node} not found in parents![/red]")
            continue
        p = end_node
        node_heat_lost = 0
        path = []
        while p:
            path.append(p)
            node_heat_lost += p.heat_lost
            p = parents[p.coordinates]
        path.reverse()
        for p in path:
            print(f"{p.coordinates}, {p.heat_lost}")
        print(f"total heat lost {node_heat_lost}")
        if node_heat_lost < value:
            value = node_heat_lost

    print(f"The value is {value}")


################################################################################


def part2():
    value = 0

    for line in open("input.txt").readlines():
        line = line.strip()

    print(f"The value is {value}")


if __name__ == "__main__":
    part1()
