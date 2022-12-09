from typing import NamedTuple, Sequence
from copy import copy

from dataclasses import dataclass


class Move(NamedTuple):
    direction: str
    distance: int


@dataclass
class Point:
    x: int
    y: int

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __hash__(self):
        return hash((self.x, self.y))


def are_touching(a: Point, b: Point) -> bool:
    if a.x == b.x:
        return -1 <= a.y - b.y <= 1
    elif a.y == b.y:
        return -1 <= a.x - b.x <= 1
    else:
        return (-1 <= a.y - b.y <= 1) and (-1 <= a.x - b.x <= 1)


assert are_touching(Point(1, 1), Point(1, 2))
assert are_touching(Point(1, 1), Point(2, 1))
assert are_touching(Point(1, 1), Point(2, 2))
assert not are_touching(Point(0, 1), Point(1, 3))


def where_to_move(head_: Point, tail_: Point):
    dir_x = head_.x - tail_.x
    if dir_x < 0:
        dir_x = -1
    elif dir_x > 0:
        dir_x = 1
    dir_y = head_.y - tail_.y
    if dir_y < 0:
        dir_y = -1
    elif dir_y > 0:
        dir_y = 1
    return Point(dir_x, dir_y)


def head_move_vector(direction: str, distance: int = 1) -> Point:
    if direction == "L":
        return Point(-distance, 0)
    elif direction == "R":
        return Point(distance, 0)
    elif direction == "U":
        return Point(0, distance)
    elif direction == "D":
        return Point(0, -distance)
    assert False, "not reached"


def print_board(rope: Sequence[Point]):
    BORDER = 2
    min_x = min(p.x for p in rope) - BORDER
    min_y = min(p.y for p in rope) - BORDER
    max_x = max(p.x for p in rope) + BORDER
    max_y = max(p.y for p in rope) + BORDER
    row = ["."] * (max_y - min_y + 1)
    board = [row.copy() for _ in range(min_x, max_x + 1)]
    for idx, p in enumerate(rope):
        rel_x = p.x - min_x
        rel_y = p.y - min_y
        if board[rel_x][rel_y] == ".":
            board[rel_x][rel_y] = str(idx)
    for row in board:
        print("".join(row))
    print()


def part_1():
    moves = []
    head = Point(100, 100)
    tail = Point(100, 100)
    visited_points = {copy(tail)}
    with open("input.txt") as indata:
        for line in indata:
            direction, distance = line.strip().split()
            moves.append(Move(direction, int(distance)))

    for move in moves:
        for _ in range(move.distance):
            vec = head_move_vector(move.direction)
            head += vec
            if not are_touching(head, tail):
                tail_vec = where_to_move(head, tail)
                tail += tail_vec
                visited_points.add(copy(tail))
    print(len(visited_points))


def part_2():
    moves = []
    rope = [Point(100, 100) for _ in range(10)]
    visited_points = {copy(rope[-1])}
    with open("input.txt") as indata:
        for line in indata:
            direction, distance = line.strip().split()
            moves.append(Move(direction, int(distance)))

    print_board(rope)
    for move in moves:
        for _ in range(move.distance):
            vec = head_move_vector(move.direction)
            rope[0] += vec
            for i, knot in enumerate(rope[1:], 1):
                if not are_touching(rope[i-1], knot):
                    knot_move_vec = where_to_move(rope[i-1], knot)
                    knot += knot_move_vec
                else:  # no need to check the rest if this knot didn't move
                    break
            visited_points.add(copy(rope[-1]))
            print_board(rope)
    print(len(visited_points))


if __name__ == '__main__':
    part_2()
