from functools import partial
from typing import Literal

from tqdm.rich import tqdm
from rich import print

from utils import Point

# Map layout (map to cube side mapping)

#  (x=1,y=2*edge+1)
#   ┊   (x=edge+1,y=1)
#   ┊   ┊   (x=2*edge+1,y=1)
#   ┊   ┊   ┊   (x=3*edge+1,y=1)
#   ┊   ┊   ┊   ┊
#   ┊   ┌───┬───┐
#   ┊   │ 1 │ 2 │
#   ┊   ├───┼───┘┈┈(x=3*edge+1,y=edge+1)
#   ┊   │ 3 │
#   ┌───┼───┤┈┈┈┈┈┈(x=3*edge+1,y=2*edge+1)
#   │ 5 │ 4 │
#   ├───┼───┘
#   │ 6 │
#   └───┘┈┈┈┈┈┈┈┈┈┈(x=edge+1,y=4*edge+1)


VERBOSE = 1
TEST_DATA = False

EMPTY = " "
WALL = "#"
OPEN_TILE = "."

# heading
HEADING = Literal["^", "v", "<", ">"]
UP: HEADING = "^"
DOWN: HEADING = "v"
RIGHT: HEADING = ">"
LEFT: HEADING = "<"

if TEST_DATA:
    CUBE_EDGE = 10
else:
    CUBE_EDGE = 50

rotation = {
    UP: {"R": RIGHT, "L": LEFT},
    DOWN: {"R": LEFT, "L": RIGHT},
    LEFT: {"R": UP, "L": DOWN},
    RIGHT: {"R": DOWN, "L": UP},
}


def load_input() -> tuple[list[list[str]], list[int | str]]:
    with open("test_input.txt" if TEST_DATA else "input.txt") as indata:
        map_ = [[""]]  # rows start at 1 so insert a dummy row
        route = ""
        reading_map = True
        for line in indata:
            if line.strip() == "":
                reading_map = False
                continue
            line = line.rstrip()
            if reading_map:
                map_.append([EMPTY] + list(line))  # columns start 1 so insert a dummy column
            else:
                route = line
    instructions: list[int | str] = []
    number = ""
    while route:
        char = route[0]
        route = route[1:]
        if char.isnumeric():
            number += char
        else:
            if number:
                instructions.append(int(number))
                number = ""
            instructions.append(char)
    if number:
        instructions.append(int(number))

    return map_, instructions


def find_starting_point(map) -> Point:
    return Point(map[1].index(OPEN_TILE), 1)


def print_map(map_, route_taken: list[tuple[Point, HEADING]], final_heading: HEADING):
    canvas = []
    for r, row in enumerate(map_):
        canvas_row = []
        for c, cell in enumerate(row):
            if cell == EMPTY:
                canvas_row.append(EMPTY)
            elif cell == WALL:
                canvas_row.append("[blue]\N{FULL BLOCK}[/blue]")
            elif cell == OPEN_TILE:
                canvas_row.append(f"[white]{OPEN_TILE}[/white]")
        canvas.append(canvas_row)

    for point, heading in route_taken:
        canvas[point.y][point.x] = f"[green]{heading}[/green]"

    canvas[point.y][point.x] = f"[red]{final_heading}[/red]"
    print("     " + "0123456789" * 11)
    for r, row in enumerate(canvas):
        print(f"{r:3}: {''.join(row)}")


def move(map: list[list[str]], current_position: Point, heading: HEADING, amount: int):
    route_taken = []
    for _ in range(amount):
        if heading == UP:
            destination = Point(current_position.x, current_position.y - 1)
            if (
                destination.y == 0
                or destination.x >= len(map[destination.y])
                or map[destination.y][destination.x] == EMPTY
            ):  # wrap around
                for y in range(len(map) - 1, current_position.y, -1):
                    if destination.x < len(map[y]) and map[y][destination.x] != EMPTY:
                        destination = Point(current_position.x, y)
                        break
        elif heading == DOWN:
            destination = Point(current_position.x, current_position.y + 1)
            if (
                destination.y == len(map)
                or destination.x >= len(map[destination.y])
                or map[destination.y][destination.x] == EMPTY
            ):  # wrap around
                for y in range(current_position.y):
                    if destination.x < len(map[y]) and map[y][destination.x] != EMPTY:
                        destination = Point(current_position.x, y)
                        break
        elif heading == RIGHT:
            destination = Point(current_position.x + 1, current_position.y)
            if destination.x == len(map[destination.y]) or map[destination.y][destination.x] == EMPTY:  # wrap around
                for x in range(0, current_position.x):
                    if map[destination.y][x] != EMPTY:
                        destination = Point(x, current_position.y)
                        break
        elif heading == LEFT:
            destination = Point(current_position.x - 1, current_position.y)
            if destination.x == 0 or map[destination.y][destination.x] == EMPTY:  # wrap around
                for x in range(len(map[current_position.y]) - 1, current_position.x, -1):
                    if map[destination.y][x] != EMPTY:
                        destination = Point(x, current_position.y)
                        break
        if map[destination.y][destination.x] == WALL:
            break
        current_position = destination
        route_taken.append((destination, heading))
    return current_position, route_taken


def part_1():
    map, instructions = load_input()
    current_position = start = find_starting_point(map)
    heading: HEADING = RIGHT
    route_taken = [(start, heading)]
    if VERBOSE:
        print_map(map, route_taken, heading)
        print(instructions)
    for instruction in tqdm(instructions):
        if isinstance(instruction, int):
            current_position, extra_route = move(map, current_position, heading, instruction)
            route_taken.extend(extra_route)
        else:
            heading = rotation[heading][instruction]
        if VERBOSE:
            print_map(map, route_taken, heading)
    facing_score = {RIGHT: 0, DOWN: 1, LEFT: 2, UP: 3}
    print(f"part 1 result: {1000 * current_position.y + 4*current_position.x + facing_score[heading]}")


def point_to_cube_side(point: Point) -> int:
    # 5,6
    if point.x <= CUBE_EDGE:
        if point.y >= 3 * CUBE_EDGE + 1:
            return 6
        else:
            return 5
    # 1, 3, 4
    elif CUBE_EDGE + 1 <= point.x <= 2 * CUBE_EDGE:
        if point.y <= CUBE_EDGE:
            return 1
        elif CUBE_EDGE + 1 <= point.y <= 2 * CUBE_EDGE:
            return 3
        else:
            return 4
    elif point.x >= 2 * CUBE_EDGE + 1:
        return 2


def side_point_0(side: int) -> Point:
    if side == 1:
        return Point(CUBE_EDGE + 1, 1)
    elif side == 2:
        return Point(2 * CUBE_EDGE + 1, 1)
    elif side == 3:
        return Point(CUBE_EDGE + 1, CUBE_EDGE + 1)
    elif side == 4:
        return Point(CUBE_EDGE + 1, 2 * CUBE_EDGE + 1)
    elif side == 5:
        return Point(1, 2 * CUBE_EDGE + 1)
    elif side == 6:
        return Point(1, 3 * CUBE_EDGE + 1)


def point_to_side_relative_point(p: Point, side: int) -> Point:
    if side == 1:
        return Point(p.x - CUBE_EDGE - 1, p.y - 1)
    elif side == 2:
        return Point(p.x - 2 * CUBE_EDGE - 1, p.y - 1)
    elif side == 3:
        return Point(p.x - CUBE_EDGE - 1, p.y - CUBE_EDGE - 1)
    elif side == 4:
        return Point(p.x - 2 * CUBE_EDGE - 1, p.y - 2 * CUBE_EDGE - 1)
    elif side == 5:
        return Point(p.x - 1, p.y - 2 * CUBE_EDGE - 1)
    elif side == 6:
        return Point(p.x - 1, p.y - 3 * CUBE_EDGE - 1)


def move_to_other_side(src_cube_side: int, current_position: Point, heading: HEADING) -> tuple[Point, HEADING]:
    def rotate90(p: Point, new_side: int) -> Point:
        p0 = side_point_0(new_side)
        return Point(p0.x + p.y, p0.y + p.x)

    def rotate180(p: Point, new_side: int) -> Point:
        p0 = side_point_0(new_side)
        return Point(p0.x + p.x, p0.y + CUBE_EDGE - p.y - 1)

    def rotate270(p: Point, new_side: int) -> Point:
        p0 = side_point_0(new_side)
        return Point(p0.x + p.y, p0.y + p.x)

    def from_bottom(p: Point, new_side: int) -> Point:
        p0 = side_point_0(new_side)
        return Point(p0.x + p.x, p0.y + CUBE_EDGE - 1)

    def from_top(p: Point, new_side: int) -> Point:
        p0 = side_point_0(new_side)
        return Point(p0.x + p.x, p0.y + 0)

    def from_left(p: Point, new_side: int) -> Point:
        p0 = side_point_0(new_side)
        return Point(p0.x + 0, p0.y + p.y)

    def from_right(p: Point, new_side: int) -> Point:
        p0 = side_point_0(new_side)
        return Point(p0.x + CUBE_EDGE, p0.y + p.y)

    new_heading = {
        1: {
            UP: {"new heading": RIGHT, "transformation": partial(rotate90, new_side=6), "new_side": 6},
            DOWN: {"new heading": DOWN, "transformation": partial(from_top, new_side=3), "new_side": 3},
            LEFT: {"new heading": RIGHT, "transformation": partial(rotate180, new_side=5), "new_side": 5},
            RIGHT: {"new heading": RIGHT, "transformation": partial(from_left, new_side=2), "new_side": 2},
        },
        2: {
            UP: {"new heading": UP, "transformation": partial(from_bottom, new_side=6), "new_side": 6},
            DOWN: {"new heading": LEFT, "transformation": partial(rotate90, new_side=3), "new_side": 3},
            LEFT: {"new heading": LEFT, "transformation": partial(from_right, new_side=5), "new_side": 5},
            RIGHT: {"new heading": LEFT, "transformation": partial(rotate180, new_side=4), "new_side": 4},
        },
        3: {
            UP: {"new heading": UP, "transformation": partial(from_bottom, new_side=1), "new_side": 1},
            DOWN: {"new heading": DOWN, "transformation": partial(from_top, new_side=4), "new_side": 4},
            LEFT: {"new heading": DOWN, "transformation": partial(rotate270, new_side=5), "new_side": 5},
            RIGHT: {"new heading": UP, "transformation": partial(rotate270, new_side=2), "new_side": 2},
        },
        4: {
            UP: {"new heading": UP, "transformation": partial(from_bottom, new_side=3), "new_side": 3},
            DOWN: {"new heading": LEFT, "transformation": partial(rotate90, new_side=6), "new_side": 6},
            LEFT: {"new heading": LEFT, "transformation": partial(from_right, new_side=5), "new_side": 5},
            RIGHT: {"new heading": LEFT, "transformation": partial(rotate180, new_side=2), "new_side": 2},
        },
        5: {
            UP: {"new heading": RIGHT, "transformation": partial(rotate90, new_side=3), "new_side": 3},
            DOWN: {"new heading": DOWN, "transformation": partial(from_top, new_side=6), "new_side": 6},
            LEFT: {"new heading": RIGHT, "transformation": partial(rotate180, new_side=1), "new_side": 1},
            RIGHT: {"new heading": RIGHT, "transformation": partial(from_left, new_side=4), "new_side": 4},
        },
        6: {
            UP: {"new heading": UP, "transformation": partial(from_bottom, new_side=5), "new_side": 5},
            DOWN: {"new heading": DOWN, "transformation": partial(from_top, new_side=2), "new_side": 2},
            LEFT: {"new heading": DOWN, "transformation": partial(rotate270, new_side=1), "new_side": 1},
            RIGHT: {"new heading": UP, "transformation": partial(rotate270, new_side=4), "new_side": 4},
        },
    }

    return (
        new_heading[src_cube_side][heading]["transformation"](
            point_to_side_relative_point(current_position, src_cube_side)
        ),
        new_heading[src_cube_side][heading]["new heading"],
    )


def move2(map: list[list[str]], current_position: Point, heading: HEADING, amount: int):
    route_taken = []
    for _ in range(amount):
        src_cube_side = point_to_cube_side(current_position)
        if heading == UP:
            destination = Point(current_position.x, current_position.y - 1)
            if (
                destination.y == 0
                or destination.x >= len(map[destination.y])
                or map[destination.y][destination.x] == EMPTY
            ):  # wrap around
                destination, heading = move_to_other_side(src_cube_side, current_position, heading)
        elif heading == DOWN:
            destination = Point(current_position.x, current_position.y + 1)
            if (
                destination.y == len(map)
                or destination.x >= len(map[destination.y])
                or map[destination.y][destination.x] == EMPTY
            ):  # wrap around
                destination, heading = move_to_other_side(src_cube_side, current_position, heading)
        elif heading == RIGHT:
            destination = Point(current_position.x + 1, current_position.y)
            if destination.x == len(map[destination.y]) or map[destination.y][destination.x] == EMPTY:  # wrap around
                destination, heading = move_to_other_side(src_cube_side, current_position, heading)
        elif heading == LEFT:
            destination = Point(current_position.x - 1, current_position.y)
            if destination.x == 0 or map[destination.y][destination.x] == EMPTY:  # wrap around
                destination, heading = move_to_other_side(src_cube_side, current_position, heading)
        if map[destination.y][destination.x] == WALL:
            break
        assert destination.x > 0 and destination.y > 0
        current_position = destination

        route_taken.append((destination, heading))
    return current_position, heading, route_taken


def part_2():
    map_, instructions = load_input()
    current_position = start = find_starting_point(map_)
    heading: HEADING = RIGHT
    route_taken = [(start, heading)]
    if VERBOSE >= 1:
        print_map(map_, route_taken, heading)
    if VERBOSE >= 2:
        print(instructions)
    if VERBOSE:
        iterable = instructions
    else:
        iterable = tqdm(instructions)
    for instruction in iterable:
        if isinstance(instruction, int):
            current_position, heading, extra_route = move2(map_, current_position, heading, instruction)
            route_taken.extend(extra_route)
        else:
            heading = rotation[heading][instruction]
        if VERBOSE >= 2:
            print_map(map_, route_taken, heading)
    if VERBOSE >= 1:
        print_map(map_, route_taken, heading)
    facing_score = {RIGHT: 0, DOWN: 1, LEFT: 2, UP: 3}
    print(f"part 2 result: {1000 * current_position.y + 4*current_position.x + facing_score[heading]}")


if __name__ == "__main__":
    part_2()
