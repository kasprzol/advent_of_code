from typing import Literal

from tqdm.rich import tqdm
from rich import print

from utils import Point

VERBOSE = False
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

rotation = {
    UP: {"R": RIGHT, "L": LEFT},
    DOWN: {"R": LEFT, "L": RIGHT},
    LEFT: {"R": UP, "L": DOWN},
    RIGHT: {"R": DOWN, "L": UP},
}


def load_input() -> tuple[list[list[str]], list[int | str]]:
    with open("input.txt") as indata:
        map = [[""]]  # rows start at 1 so insert a dummy row
        route = ""
        reading_map = True
        for line in indata:
            if line.strip() == "":
                reading_map = False
                continue
            line = line.rstrip()
            if reading_map:
                map.append([EMPTY] + list(line))  # columns start 1 so insert a dummy column
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

    return map, instructions


def find_starting_point(map) -> Point:
    return Point(map[1].index(OPEN_TILE), 1)


def print_map(map, route_taken: list[tuple[Point, HEADING]], final_heading: HEADING):
    canvas = []
    for r, row in enumerate(map):
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
                for y in range(0, current_position.y):
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


if __name__ == "__main__":
    part_1()
