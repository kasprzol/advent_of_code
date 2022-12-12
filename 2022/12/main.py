from collections import defaultdict
import  heapq


class Node:

    def __init__(self, height, coordinates):
        self.height = height
        self.coordinates = coordinates
        self.links: list[tuple[int, int]] = []

    def __repr__(self):
        return f"Point({self.height} at {self.coordinates})"

    def __lt__(self, other):
        return self.coordinates < other.coordinates


def build_graph(input_map):
    start = None
    end = None
    coordinates_to_graph: dict[tuple[int, int], Node] = {}
    for row_idx, row in enumerate(input_map):
        graph_row = []
        for col, point in enumerate(row):
            coordinates = (row_idx, col)
            node = Node(point, coordinates)
            graph_row.append(node)
            coordinates_to_graph[coordinates] = node
            if point == "S":
                point = "a"
                input_map[row_idx][col] = "a"
                start = node
            elif point == "E":
                point = "z"
                input_map[row_idx][col] = "z"
                end = node

            height_current = ord(point)
            height_top = ord(input_map[row_idx - 1][col])
            if row_idx > 0 and height_top <= 1 + height_current:
                node.links.append((row_idx - 1, col))
            if row_idx < len(input_map) - 1:
                height_bottom = ord(input_map[row_idx + 1][col])
                if height_bottom <= 1 + height_current:
                    node.links.append((row_idx + 1, col))
            height_left = ord(input_map[row_idx][col - 1])
            if col > 0 and height_left <= 1 + height_current:
                node.links.append((row_idx, col - 1))
            if col < len(row) - 1:
                height_right = ord(input_map[row_idx][col + 1])
                if height_right <= 1 + height_current:
                    node.links.append((row_idx, col + 1))
    return coordinates_to_graph, start, end


def build_graph2(input_map):
    start = []
    end = None
    coordinates_to_graph: dict[tuple[int, int], Node] = {}
    for row_idx, row in enumerate(input_map):
        graph_row = []
        for col, point in enumerate(row):
            coordinates = (row_idx, col)
            node = Node(point, coordinates)
            graph_row.append(node)
            coordinates_to_graph[coordinates] = node
            if point in ("a", "S"):
                point = "a"
                input_map[row_idx][col] = "a"
                start.append(node)
            elif point == "E":
                point = "z"
                input_map[row_idx][col] = "z"
                end = node

            height_current = ord(point)
            height_top = ord(input_map[row_idx - 1][col])
            if row_idx > 0 and height_top <= 1 + height_current:
                node.links.append((row_idx - 1, col))
            if row_idx < len(input_map) - 1:
                height_bottom = ord(input_map[row_idx + 1][col])
                if height_bottom <= 1 + height_current:
                    node.links.append((row_idx + 1, col))
            height_left = ord(input_map[row_idx][col - 1])
            if col > 0 and height_left <= 1 + height_current:
                node.links.append((row_idx, col - 1))
            if col < len(row) - 1:
                height_right = ord(input_map[row_idx][col + 1])
                if height_right <= 1 + height_current:
                    node.links.append((row_idx, col + 1))
    return coordinates_to_graph, start, end


def load_input():
    height_map = []
    with open("input.txt") as indata:
        for line in indata:
            line = line.strip()
            height_map.append(list(line))
    return height_map


def dijkstra(graph: dict[tuple[int, int], Node], start: Node, end: Node) -> dict[tuple[int, int], Node]:
    distance = defaultdict(lambda: 99_999_999)
    distance[start.coordinates] = 0
    parent: dict[tuple[int, int], Node] = {start.coordinates: None}
    queue: list[tuple[int, Node]] = [(0, start)]
    heapq.heappush(queue, (9999_9999_9999_9999, end))
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
    height_map = load_input()
    graph, start, end = build_graph(height_map)
    parents = dijkstra(graph, start, end)
    visual = [["." for _ in range(len(height_map[0]))] for _ in range(len(height_map))]
    way = [end.coordinates]
    foo = end.coordinates
    while foo != start.coordinates:
        foo = parents[foo].coordinates
        way.append(foo)
    way.reverse()
    for idx, point in enumerate(way):
        direction = ""
        if point != end.coordinates:
            pr, pc = point
            nextr, nextc = way[idx + 1]
            if (pr + 1, pc) == (nextr, nextc):
                direction = "\N{DOWNWARDS ARROW}"
            elif (pr, pc + 1) == (nextr, nextc):
                direction = "\N{RIGHTWARDS ARROW}"
            elif (pr - 1, pc) == (nextr, nextc):
                direction = "\N{UPWARDS ARROW}"
            elif (pr, pc - 1) == (nextr, nextc):
                direction = "\N{LEFTWARDS ARROW}"
            visual[pr][pc] = direction
    for line in visual:
        print("".join(line))


def part_2():
    height_map = load_input()
    graph, starts, end = build_graph2(height_map)
    shortest = 99999_99999
    for s in starts:
        try:
            p = dijkstra(graph, s, end)

            way = [end.coordinates]
            foo = end.coordinates
            while foo != s.coordinates:
                foo = p[foo].coordinates
                way.append(foo)
            if shortest > len(way) - 1:
                shortest = len(way) - 1
                start = s
                parents = p
        except KeyError as e:
            print(f"Couldn't find a way from {s}")
            continue
    print(shortest)

    visual = [["." for _ in range(len(height_map[0]))] for _ in range(len(height_map))]
    way = [end.coordinates]
    foo = end.coordinates
    while foo != start.coordinates:
        foo = parents[foo].coordinates
        way.append(foo)
    way.reverse()
    for idx, point in enumerate(way):
        direction = ""
        if point != end.coordinates:
            pr, pc = point
            nextr, nextc = way[idx + 1]
            if (pr + 1, pc) == (nextr, nextc):
                direction = "\N{DOWNWARDS ARROW}"
            elif (pr, pc + 1) == (nextr, nextc):
                direction = "\N{RIGHTWARDS ARROW}"
            elif (pr - 1, pc) == (nextr, nextc):
                direction = "\N{UPWARDS ARROW}"
            elif (pr, pc - 1) == (nextr, nextc):
                direction = "\N{LEFTWARDS ARROW}"
            visual[pr][pc] = direction
    for line in visual:
        print("".join(line))


if __name__ == '__main__':
    part_2()
