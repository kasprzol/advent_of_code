from collections import defaultdict
from dataclasses import dataclass, field
from typing import Literal, Iterable
import heapq

from tqdm.rich import tqdm
from rich import print

from utils import Point, Point3d

VERBOSE = 1
TEST_DATA = False

EMPTY = "."
WALL = "#"
MAX_TIME = 512

if TEST_DATA:
    ...
else:
    ...


def load_input() -> list[list[str]]:
    with open("test_input.txt" if TEST_DATA else "input.txt") as indata:
        valey_map = [list(line.strip()) for line in indata]

    winds = {}
    for r, row in enumerate(valey_map):
        for c, cell in enumerate(row):
            if cell in ["^", "v", ">", "<"]:
                winds[Point(c, r)] = cell

    return valey_map, winds


def find_starting_point(valey_map):
    for idx, cell in enumerate(valey_map[0]):
        if cell == EMPTY:
            start = Point(idx, 0)
            break

    for idx, cell in enumerate(valey_map[-1]):
        if cell == EMPTY:
            end = Point(idx, len(valey_map) - 1)
            break

    return start, end


def print_map(valey_map, winds):
    canvas = []


#     for r, row in enumerate(valey_map):
#         canvas_row = []
#         for c, cell in enumerate(row):
#             if cell == EMPTY:
#                 canvas_row.append(EMPTY)
#             elif cell == WALL:
#                 canvas_row.append("[blue]\N{FULL BLOCK}[/blue]")
#         canvas.append(canvas_row)
#
#     for point, heading in route_taken:
#         canvas[point.y][point.x] = f"[green]{heading}[/green]"
#
#     print("     " + "0123456789" * 11)
#     for r, row in enumerate(canvas):
#         print(f"{r:3}: {''.join(row)}")


def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)


def lcm(a, b):
    return (a * b) // gcd(a, b)


@dataclass
class Node:
    coordinates: Point3d
    links: list[Point3d] = field(default_factory=list)

    def __lt__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        return self.coordinates < other.coordinates


def generate_all_snapshots(valey_map, winds: dict[Point, str], start: Point, end: Point, starting_wind_cycle: int = 0):
    map_width = len(valey_map[0]) - 2  # substract the borders
    map_height = len(valey_map) - 2
    number_of_wind_cycles = lcm(map_height, map_width)
    wind_cycles = [{coord: [wind] for coord, wind in winds.items()}]
    wind_cycles.extend([defaultdict(list) for _ in range(number_of_wind_cycles - 1)])

    def clamp_wind(wind: Point):
        if wind.x == 0:
            wind = Point(map_width, wind.y)
        elif wind.x > map_width:
            wind = Point(1, wind.y)
        if wind.y == 0:
            wind = Point(wind.x, map_height)
        elif wind.y > map_height:
            wind = Point(wind.x, 1)
        return wind

    new_position = {"<": Point(-1, 0), ">": Point(1, 0), "^": Point(0, -1), "v": Point(0, 1)}
    for i in range(1, number_of_wind_cycles):
        for coord, winds in wind_cycles[i - 1].items():
            for wind in winds:
                new_coord = clamp_wind(coord + new_position[wind])
                assert wind not in wind_cycles[i][new_coord]
                wind_cycles[i][new_coord].append(wind)

    wind_cycles = deque(wind_cycles)
    wind_cycles.rotate(-starting_wind_cycle)

    nodes: list[Node] = []
    top_point = start if start.y == 0 else end
    bottom_point = end if end.y == map_height + 1 else start
    # now generate the graph of possible moves
    neighbours = (Point(-1, 0), Point(1, 0), Point(0, -1), Point(0, 1))
    for i in range(MAX_TIME):
        next_cycle = (i + 1) % len(wind_cycles)
        for x in range(1, map_width + 1):
            for y in range(0, map_height + 2):
                if (y == 0 and x != top_point.x) or (y == map_height + 1 and x != bottom_point.x):
                    continue
                node = Node(Point3d(x, y, i))
                point = Point(x, y)
                if point not in wind_cycles[next_cycle] and i + 1 < MAX_TIME:
                    node.links.append(Point3d(x, y, i + 1))
                for neighbour in neighbours:
                    n = point + neighbour
                    if (
                        (n.x <= 0 or n.x >= map_width + 1 or n.y <= 0 or n.y >= map_height + 1)
                        and (n.x != start.x or n.y != start.y)
                        and (n.x != end.x or n.y != end.y)
                    ):
                        continue
                    if n not in wind_cycles[next_cycle] and i + 1 < MAX_TIME:
                        node.links.append(Point3d(n.x, n.y, i + 1))
                # if node.links:
                for link in node.links:
                    assert link != node.coordinates
                nodes.append(node)
        # handle start & end
    start_nodes = [
        n for n in nodes if n.coordinates.x == start.x and n.coordinates.y == start.y and n.coordinates.z == 0
    ]
    end_nodes = [n for n in nodes if n.coordinates.x == end.x and n.coordinates.y == end.y]
    assert len(start_nodes) == 1
    # assert len(end_nodes) == number_of_wind_cycles + 1
    return nodes, start_nodes[0], end_nodes


def dijkstra(nodes: Iterable[Node], start: Node, end_nodes: Iterable[Node]) -> dict[Point3d, Node]:
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
            if distance[link] > distance[u.coordinates] + 1:
                distance[link] = distance[u.coordinates] + 1
                parent[link] = u
                heapq.heappush(queue, (distance[link], graph[link]))

    # foo = end.coordinates
    # way = [end]
    # while foo != start.coordinates:
    #     foo = parent[foo].coordinates
    #     way.append(foo)
    # print(f"{len(way)=}, {way}")
    # print(f"ANSWER: need to take {len(way) - 1 } steps!!")
    return parent


def part_1():
    valey_map, winds = load_input()
    start, end = find_starting_point(valey_map)
    # print_map(valey_map, winds)
    nodes, start_node, end_nodes = generate_all_snapshots(valey_map, winds, start, end)
    parents = dijkstra(nodes, start_node, end_nodes)
    paths = {}
    for end_node in end_nodes:
        end_node = end_node.coordinates
        if end_node in parents:
            paths[end_node] = []
            node = end_node
            while parents[node]:
                paths[end_node].append(node)
                node = parents[node].coordinates
            paths[end_node].reverse()
            print(f"Found a way to {end_node}")
        else:
            print(f"No way to {end_node}")

    shortest = min(paths.values(), key=len)
    print(f"shortest path: {len(shortest)} {shortest}")


def part_2():
    valey_map, winds = load_input()
    start, end = find_starting_point(valey_map)
    # print_map(valey_map, winds)
    nodes, start_node, end_nodes = generate_all_snapshots(valey_map, winds, start, end)
    parents = dijkstra(nodes, start_node, end_nodes)
    paths = {}
    for end_node in end_nodes:
        end_node = end_node.coordinates
        if end_node in parents:
            paths[end_node] = []
            node = end_node
            while parents[node]:
                paths[end_node].append(node)
                node = parents[node].coordinates
            paths[end_node].reverse()
            if VERBOSE > 1:
                print(f"Found a way to {end_node}")
        else:
            print(f"No way to {end_node}")

    shortest = min(paths.values(), key=len)
    print(f"shortest path: {len(shortest)} {shortest}")

    nodes, start_node, end_nodes = generate_all_snapshots(valey_map, winds, end, start, len(shortest))
    parents = dijkstra(nodes, start_node, end_nodes)
    paths = {}
    for end_node in end_nodes:
        end_node = end_node.coordinates
        if end_node in parents:
            paths[end_node] = []
            node = end_node
            while parents[node]:
                paths[end_node].append(node)
                node = parents[node].coordinates
            paths[end_node].reverse()
            if VERBOSE > 1:
                print(f"Found a way to {end_node}")
        else:
            print(f"No way to {end_node}")

    shortest2 = min(paths.values(), key=len)
    print(f"shortest path: {len(shortest2)} {shortest2}")

    nodes, start_node, end_nodes = generate_all_snapshots(valey_map, winds, start, end, len(shortest) + len(shortest2))
    parents = dijkstra(nodes, start_node, end_nodes)
    paths = {}
    for end_node in end_nodes:
        end_node = end_node.coordinates
        if end_node in parents:
            paths[end_node] = []
            node = end_node
            while parents[node]:
                paths[end_node].append(node)
                node = parents[node].coordinates
            paths[end_node].reverse()
            if VERBOSE > 1:
                print(f"Found a way to {end_node}")
        else:
            print(f"No way to {end_node}")

    shortest3 = min(paths.values(), key=len)
    print(f"shortest path: {len(shortest3)} {shortest3}")

    print(f"Part 2 answer: {len(shortest) + len(shortest2) + len(shortest3)}")


if __name__ == "__main__":
    part_2()
