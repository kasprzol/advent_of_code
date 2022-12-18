import gc
from itertools import cycle
from typing import NamedTuple

from dataclasses import dataclass
from enum import Enum, auto

from utils import Point

EMPTY = "."
SETTLED_ROCK_FRAGMENT = "\N{FULL BLOCK}"
MOVING_ROCK_FRAGMENT = "\N{DARK SHADE}"
# https://www.fileformat.info/info/unicode/block/block_elements/list.htm
MAX_ROCKS = 2022
CAVE_WIDTH = 7
START_X = 2
ROCK_START_CLEARANCE = 3
FLOOR = 0

TEST_DATA = False
if TEST_DATA:
    ...
else:
    pass


class Size(NamedTuple):
    height: int
    width: int


class RockType(Enum):
    LINE = auto()  # horizontal line
    PLUS = auto()
    REVERSE_L = auto()
    PIPE = auto()  # vertical line
    SQUARE = auto()


@dataclass
class Rock:
    type: RockType
    position: Point
    shapes = {
        RockType.LINE: [[SETTLED_ROCK_FRAGMENT] * 4],
        RockType.PLUS: [
            [EMPTY, SETTLED_ROCK_FRAGMENT, EMPTY],
            [SETTLED_ROCK_FRAGMENT] * 3,
            [EMPTY, SETTLED_ROCK_FRAGMENT, EMPTY],
        ],
        RockType.REVERSE_L: [
            [EMPTY, EMPTY, SETTLED_ROCK_FRAGMENT],
            [EMPTY, EMPTY, SETTLED_ROCK_FRAGMENT],
            [SETTLED_ROCK_FRAGMENT] * 3,
        ],
        RockType.PIPE: [[SETTLED_ROCK_FRAGMENT]] * 4,
        RockType.SQUARE: [[SETTLED_ROCK_FRAGMENT] * 2] * 2,
    }

    @property
    def shape(self):
        return Rock.shapes[self.type]

    @property
    def width(self):
        return ROCK_SIZE[self.type].width

    @property
    def height(self):
        return ROCK_SIZE[self.type].height


ROCKS = cycle((RockType.LINE, RockType.PLUS, RockType.REVERSE_L, RockType.PIPE, RockType.SQUARE))
ROCK_SIZE = {
    RockType.LINE: Size(1, 4),
    RockType.PLUS: Size(3, 3),
    RockType.REVERSE_L: Size(3, 3),
    RockType.PIPE: Size(4, 1),
    RockType.SQUARE: Size(2, 2),
}


class Direction(Enum):
    LEFT = auto()
    RIGHT = auto()


class Cave:
    def __init__(self):
        self.rock = None
        self.cave = [[EMPTY for _ in range(CAVE_WIDTH)] for _ in range(4)]
        """An array of cave rows, where row 0 is the flor"""

    def move_rock_horizontal(self, direction: Direction):
        rock_edge = 0 if direction == Direction.LEFT else -1
        if direction == Direction.LEFT:
            cave_position_to_check = self.rock.position.x - 1
        else:
            cave_position_to_check = self.rock.position.x + ROCK_SIZE[self.rock.type].width
        can_move = (
            (direction == Direction.LEFT and self.rock.position.x > 0)
            or (direction == Direction.RIGHT and self.rock.position.x + ROCK_SIZE[self.rock.type].width < CAVE_WIDTH)
        ) and not any(
            # block starts at the top of the cave and we go down, that's why -y
            self.cave[self.rock.position.y - y][cave_position_to_check] != EMPTY
            for y in range(self.rock.height)
            if self.rock.shape[y][rock_edge] != EMPTY
        )

        if can_move:
            self.rock.position.x += -1 if direction == Direction.LEFT else 1

    def drop_rock(self) -> bool:
        can_drop = self.rock.position.y - self.rock.height >= FLOOR and all(
            self.cave[self.rock.position.y - self.rock.height][self.rock.position.x + x] == EMPTY
            for x in range(self.rock.width)
            if self.rock.shape[self.rock.height - 1][x] != EMPTY
        )
        if can_drop:
            self.rock.position.y -= 1
        return can_drop

    def spawn_new_rock(self):
        next_rock_type = next(ROCKS)
        missing_height = (self.height + (ROCK_START_CLEARANCE + ROCK_SIZE[next_rock_type].height)) - len(self.cave)
        if missing_height > 0:
            self.cave.extend([[EMPTY for _ in range(CAVE_WIDTH)] for _ in range(missing_height)])
            self.rock = Rock(next_rock_type, Point(START_X, len(self.cave) - 1))
        if missing_height <= 0:
            self.rock = Rock(next_rock_type, Point(START_X, len(self.cave) - 1 + missing_height))

    @property
    def height(self):
        for idx, row in enumerate(self.cave):
            if all(cell == EMPTY for cell in row):
                break
        return idx

    def print(self, final=False):
        if self.height > 30 and not final:
            return
        rows = []
        for row_idx, row in enumerate(self.cave):
            r = row.copy()
            if (
                self.rock
                and self.rock.position.y - ROCK_SIZE[self.rock.type].height + 1 <= row_idx <= self.rock.position.y
            ):
                for x, foo in enumerate(self.rock.shape[self.rock.position.y - row_idx]):
                    if foo != EMPTY:
                        r[x + self.rock.position.x] = MOVING_ROCK_FRAGMENT
            rows.append(r)
        for rev_row_idx, r in enumerate(reversed(rows)):
            print(f"{len(self.cave)-rev_row_idx:4} |" + "".join(r) + "|")
        print(
            "   0 \N{BOX DRAWINGS LIGHT UP AND RIGHT}"
            + "\N{BOX DRAWINGS LIGHT HORIZONTAL}" * len(self.cave[0])
            + "\N{BOX DRAWINGS LIGHT UP AND LEFT}"
        )

    def stop_rock(self):
        width = ROCK_SIZE[self.rock.type].width
        height = ROCK_SIZE[self.rock.type].height
        for y in range(height):
            for x in range(width):
                if self.rock.shape[y][x] != EMPTY:
                    self.cave[self.rock.position.y - y][self.rock.position.x + x] = SETTLED_ROCK_FRAGMENT
        self.rock = None


def load_data() -> str:
    with open("input.txt") as indata:
        for line in indata:
            return line.strip()


def tetris(winds: str):
    cave = Cave()
    winds = cycle(winds)
    block_dropping = False
    blocks_dropped = 0

    while blocks_dropped <= MAX_ROCKS:
        if block_dropping:
            wind = next(winds)
            rock_horizontal_direction = Direction.RIGHT if wind == ">" else Direction.LEFT
            cave.move_rock_horizontal(rock_horizontal_direction)
            cave.print()
            rock_moved_down = cave.drop_rock()
            if not rock_moved_down:
                cave.stop_rock()
                block_dropping = False
        else:
            cave.spawn_new_rock()
            block_dropping = True
            blocks_dropped += 1

        cave.print()
    cave.print(True)
    print(f"Final height of the tower: {cave.height}")
    return cave.height


def part_1():
    winds = load_data()
    final_height = tetris(winds)
    print(f"part 1 result: {final_height}")


def part_2():
    pass


if __name__ == "__main__":
    print(f"default gc: {gc.get_threshold()}")
    gc.set_threshold(267_829, 38_342, 16_893)
    part_1()
