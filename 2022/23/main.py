from collections import defaultdict, deque
from functools import partial
from operator import attrgetter
from typing import Literal, Optional

from tqdm.rich import tqdm
from rich import print

from utils import Point


VERBOSE = 0
TEST_DATA = False

ELF = "#"
EMPTY = "."


def load_input() -> list[Point]:
    elf_input = "#"
    with open("test_input.txt" if TEST_DATA else "input.txt") as indata:
        elves: list[Point] = []
        for row_idx, line in enumerate(indata):
            line = line.strip()
            if line == "":
                break
            elves.extend(Point(col, row_idx) for col, spot in enumerate(line) if spot == elf_input)

    return elves


def print_map(map_: defaultdict[int, defaultdict[int, Point | None]], highlight: Optional[Point] = None, want_to_move_to = None):
    canvas = []
    min_x = 0
    max_x = 0
    min_y = 0
    max_y = 0
    for x in map_:
        for y in map_[x]:
            if y > max_y:
                max_y = y
            if y < min_y:
                min_y = y
        if x > max_x:
            max_x = x
        if x < min_x:
            min_x = x
    for y in range(min_y, max_y + 1):
        canvas_row = []
        for x in range(min_x, max_x + 1):
            if y in map_[x] and map_[x][y] is not None:
                if highlight and highlight == Point(x, y):
                    canvas_row.append("[yellow]\N{FULL BLOCK}[/yellow]")
                else:
                    canvas_row.append("[red]#[/red]")
            else:
                canvas_row.append(f"[white]{EMPTY}[/white]")
        canvas.append(canvas_row)

    want_to_move_to = want_to_move_to or {}
    for elves in want_to_move_to.values():
        for elf, arrow in elves:
            y = elf.y - min_y
            x = elf.x-min_x
            if highlight and highlight == Point(x, y):
                canvas[y][x] = f"[yellow]{arrow}[/yellow]"
            else:
                canvas[y][x] = f"[red]{arrow}[/red]"

    if min_x < 0:
        negatives = "9876543210" * 4
        negatives = f"[purple]-{negatives[min_x - 1 :]}[/purple]"
    else:
        negatives = " 0"

    print(f"    {negatives}" + "123456789" * 4)
    r = min_y
    for row in canvas:
        print(f"{r:3}: {''.join(row)}")
        r += 1

def direction_to_arrow(direction: tuple[int, int]):
    match direction:
        case (0, -1):
            return "\N{UPWARDS ARROW}"
        case (0, 1):
            return "\N{DOWNWARDS ARROW}"
        case ( -1,0):
            return "\N{LEFTWARDS ARROW}"
        case ( 1,0):
            return "\N{RIGHTWARDS ARROW}"


def part_1():
    elves = load_input()
    map_ = generate_map(elves)
    num_rounds = 10
    if VERBOSE:
        print_map(map_)

    # N, NE, NW == (0, -1), (-1, -1), (1, -1)
    possible_move_directions = deque(
        [
            # where to move; what directions to check before moving
            ((0, -1), ((0, -1), (-1, -1), (1, -1))),  # N
            ((0, 1), ((0, 1), (-1, 1), (1, 1))),      # S
            ((-1, 0), ((-1, 0), (-1, -1), (-1, 1))),  # W
            ((1, 0), ((1, 0), (1, -1), (1, 1))),      # E
        ]
    )

    for round_num in tqdm(range(num_rounds)):
        want_to_move_to = defaultdict(list)
        if VERBOSE:
            print(f"Round {round_num + 1}, move directions: {[direction_to_arrow(d[0]) for d in possible_move_directions]}")
            print_map(map_)
        for elf in elves:
            if VERBOSE > 1:
                print_map(map_, elf, want_to_move_to)
            has_neighbours = any(
                map_[x][y] is not None
                for x in range(elf.x - 1, elf.x + 2)
                for y in range(elf.y - 1, elf.y + 2)
                if Point(x, y) != elf
            )
            if has_neighbours:
                # this elf wants to move
                for direction, to_check in possible_move_directions:
                    next_direction = any(map_[elf.x + subdir[0]][elf.y + subdir[1]] is not None for subdir in to_check)
                    if next_direction:
                        continue
                    # no other elf there, move in that direction
                    want_to_move_to[(elf.x + direction[0], elf.y + direction[1])].append((elf, direction_to_arrow(direction)))
                    break
                else:
                    if VERBOSE > 1:
                        print(f"The elf at {elf} wants to move but has nowhere to go")
        # move all the elves that want to move
        if VERBOSE:
            print(want_to_move_to)

        for destination, moving_elves in want_to_move_to.items():
            if len(moving_elves) > 1:
                # more than 1 elf wants to move to this destination, no one moves.
                continue
            # move the elf to this destination
            new_elf = Point(*destination)
            elf_idx = elves.index(moving_elves[0][0])
            elves[elf_idx] = new_elf

        map_ = generate_map(elves)
        possible_move_directions.rotate(-1)
        if VERBOSE:
            print(f"End of Round {round_num + 1}")
            print_map(map_)

    # calculate number of empty ground
    min_x = 0
    max_x = 0
    min_y = 0
    max_y = 0
    for x in map_:
        for y in map_[x]:
            if y > max_y:
                max_y = y
            if y < min_y:
                min_y = y
        if x > max_x:
            max_x = x
        if x < min_x:
            min_x = x
    print(sum(1 if map_[x][y] is None else 0 for x in range(min_x, max_x+1) for y in range(min_y,max_y+1)))



def generate_map(elves: list[Point]) -> defaultdict[int, defaultdict[int, Point | None]]:
    map_: defaultdict[int, defaultdict[int, Point | None]] = defaultdict(lambda: defaultdict(lambda: None))
    for elf in elves:
        map_[elf.x][elf.y] = elf
    return map_

def part_2():
    elves = load_input()
    map_ = generate_map(elves)
    num_rounds = 10
    if VERBOSE:
        print_map(map_)

    # N, NE, NW == (0, -1), (-1, -1), (1, -1)
    possible_move_directions = deque(
        [
            # where to move; what directions to check before moving
            ((0, -1), ((0, -1), (-1, -1), (1, -1))),  # N
            ((0, 1), ((0, 1), (-1, 1), (1, 1))),      # S
            ((-1, 0), ((-1, 0), (-1, -1), (-1, 1))),  # W
            ((1, 0), ((1, 0), (1, -1), (1, 1))),      # E
        ]
    )

    round_num = 0
    while True:
        round_num +=1
        want_to_move_to = defaultdict(list)
        if VERBOSE:
            print(f"Round {round_num}, move directions: {[direction_to_arrow(d[0]) for d in possible_move_directions]}")
            print_map(map_)
        for elf in elves:
            if VERBOSE > 1:
                print_map(map_, elf, want_to_move_to)
            has_neighbours = any(
                map_[x][y] is not None
                for x in range(elf.x - 1, elf.x + 2)
                for y in range(elf.y - 1, elf.y + 2)
                if Point(x, y) != elf
            )
            if has_neighbours:
                # this elf wants to move
                for direction, to_check in possible_move_directions:
                    next_direction = any(map_[elf.x + subdir[0]][elf.y + subdir[1]] is not None for subdir in to_check)
                    if next_direction:
                        continue
                    # no other elf there, move in that direction
                    want_to_move_to[(elf.x + direction[0], elf.y + direction[1])].append((elf, direction_to_arrow(direction)))
                    break
                else:
                    if VERBOSE > 1:
                        print(f"The elf at {elf} wants to move but has nowhere to go")
        # move all the elves that want to move
        if VERBOSE:
            print(want_to_move_to)

        if not want_to_move_to:
            print(f"No elf want to move on round {round_num}.")
            return
        for destination, moving_elves in want_to_move_to.items():
            if len(moving_elves) > 1:
                # more than 1 elf wants to move to this destination, no one moves.
                continue
            # move the elf to this destination
            new_elf = Point(*destination)
            elf_idx = elves.index(moving_elves[0][0])
            elves[elf_idx] = new_elf

        map_ = generate_map(elves)
        possible_move_directions.rotate(-1)
        print(f"End of Round {round_num}")
        if VERBOSE:
            print(f"End of Round {round_num}")
            print_map(map_)




if __name__ == "__main__":
    part_2()
