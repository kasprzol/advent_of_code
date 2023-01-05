import gc
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum, auto
from itertools import cycle, pairwise, repeat
from typing import NamedTuple

from rich import print
from tqdm.rich import tqdm

from utils import MutablePoint

EMPTY = "."
SETTLED_ROCK_FRAGMENT = "\N{FULL BLOCK}"
MOVING_ROCK_FRAGMENT = "\N{DARK SHADE}"
# https://www.fileformat.info/info/unicode/block/block_elements/list.htm
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
    position: MutablePoint
    shapes = {
        RockType.LINE: [[f"[red]{SETTLED_ROCK_FRAGMENT}[/red]"] * 4],
        RockType.PLUS: [
            [EMPTY, f"[green]{SETTLED_ROCK_FRAGMENT}[/green]", EMPTY],
            [f"[green]{SETTLED_ROCK_FRAGMENT}[/green]"] * 3,
            [EMPTY, f"[green]{SETTLED_ROCK_FRAGMENT}[/green]", EMPTY],
        ],
        RockType.REVERSE_L: [
            [EMPTY, EMPTY, f"[yellow]{SETTLED_ROCK_FRAGMENT}[/yellow]"],
            [EMPTY, EMPTY, f"[yellow]{SETTLED_ROCK_FRAGMENT}[/yellow]"],
            [f"[yellow]{SETTLED_ROCK_FRAGMENT}[/yellow]"] * 3,
        ],
        RockType.PIPE: [[f"[blue]{SETTLED_ROCK_FRAGMENT}[/blue]"]] * 4,
        RockType.SQUARE: [[f"[purple]{SETTLED_ROCK_FRAGMENT}[/purple]"] * 2] * 2,
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
        self.cave = [[EMPTY for _ in range(CAVE_WIDTH)] for __ in range(4)]
        """An array of cave rows, where row 0 is the flor"""

    def move_rock_horizontal(self, direction: Direction):
        cave_offset = -1 if direction == Direction.LEFT else 1
        can_move = (
            (direction == Direction.LEFT and self.rock.position.x > 0)
            or (direction == Direction.RIGHT and self.rock.position.x + ROCK_SIZE[self.rock.type].width < CAVE_WIDTH)
        ) and all(
            # block starts at the top of the cave and we go down, that's why -y
            self.cave[self.rock.position.y - y][self.rock.position.x + x + cave_offset] == EMPTY
            for y in range(self.rock.height)
            for x in range(self.rock.width)
            if self.rock.shape[y][x] != EMPTY
        )

        if can_move:
            self.rock.position.x += -1 if direction == Direction.LEFT else 1

    def drop_rock(self) -> bool:
        can_drop = self.rock.position.y - self.rock.height >= FLOOR and all(
            self.cave[self.rock.position.y - y - 1][self.rock.position.x + x] == EMPTY
            for y in range(self.rock.height)
            for x in range(self.rock.width)
            if self.rock.shape[y][x] != EMPTY
        )
        if can_drop:
            self.rock.position.y -= 1
        return can_drop

    def spawn_new_rock(self):
        next_rock_type = next(ROCKS)
        missing_height = (self.height + (ROCK_START_CLEARANCE + ROCK_SIZE[next_rock_type].height)) - len(self.cave)
        if missing_height > 0:
            self.cave.extend([[EMPTY for _ in range(CAVE_WIDTH)] for __ in range(missing_height)])
            self.rock = Rock(next_rock_type, MutablePoint(START_X, len(self.cave) - 1))
        if missing_height <= 0:
            self.rock = Rock(
                next_rock_type,
                MutablePoint(START_X, len(self.cave) - 1 + missing_height),
            )

    @property
    def height(self):
        h = len(self.cave)
        for row in reversed(self.cave):
            if any(cell != EMPTY for cell in row):
                break
            h -= 1
        return h

    def print(self, final=False):
        if self.height > 105 and not final:
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
                    self.cave[self.rock.position.y - y][self.rock.position.x + x] = self.rock.shape[y][x]
        self.rock = None


def load_data() -> str:
    with open("test_input.txt" if TEST_DATA else "input.txt") as indata:
        for line in indata:
            return line.strip()


def tetris(winds: str, max_rocks: int):
    cave = Cave()
    winds = cycle(winds)
    block_dropping = False
    blocks_dropped = 0

    progress = iter(tqdm(repeat(1), total=max_rocks))
    while blocks_dropped <= max_rocks:
        if block_dropping:
            wind = next(winds)
            rock_horizontal_direction = Direction.RIGHT if wind == ">" else Direction.LEFT
            cave.move_rock_horizontal(rock_horizontal_direction)
            # cave.print()
            rock_moved_down = cave.drop_rock()
            if not rock_moved_down:
                cave.stop_rock()
                block_dropping = False
        else:
            cave.spawn_new_rock()
            block_dropping = True
            blocks_dropped += 1
            next(progress)

        # cave.print()
    # cave.print(True)
    print(f"Final height of the tower: {cave.height}")
    return cave.height


class CaveSnapshot(NamedTuple):
    height: int
    cave_state: list
    rocks_dropped: int


class Cycle(NamedTuple):
    rock_type: RockType
    wind_idx: int
    height: int
    rocks_dropped: int


def tetris2(winds_input: str, max_rocks: int, height_to_start_searching_for_cycles: int):
    cave = Cave()
    winds = cycle(enumerate(winds_input))
    block_dropping = False
    blocks_dropped = wind_idx = 0

    tetris_cycle = defaultdict(list)
    found_cycle = None
    cycle_applied = False
    progress = iter(tqdm(repeat(1), total=max_rocks))
    while blocks_dropped <= max_rocks:
        if block_dropping:
            wind_idx, wind = next(winds)
            rock_horizontal_direction = Direction.RIGHT if wind == ">" else Direction.LEFT
            cave.move_rock_horizontal(rock_horizontal_direction)
            # cave.print()
            rock_moved_down = cave.drop_rock()
            if not rock_moved_down:
                cave.stop_rock()
                block_dropping = False
        else:
            cave.spawn_new_rock()
            block_dropping = True
            blocks_dropped += 1
            next(progress)
            # add board, wind, and next rock state to cycle detection
            cave_height_for_snapshot = 400
            cave_height_to_skip = 600 if TEST_DATA else 1_500  # skip before starting to look for cycles
            if not found_cycle and cave.rock and cave.height > cave_height_to_skip:
                tetris_cycle[(cave.rock.type, wind_idx % len(winds_input))].append(
                    CaveSnapshot(
                        cave.height,
                        deepcopy(cave.cave[cave.height - cave_height_for_snapshot :]),
                        blocks_dropped,
                    )
                )

            if (
                found_cycle
                and not cycle_applied
                and cave.rock.type == found_cycle.rock_type
                and wind_idx % len(winds_input) == found_cycle.wind_idx
            ):
                # we're at the start of the cycle
                missing_rocks = max_rocks - (blocks_dropped - 1)  # -1 as don't count the newly spawned rock
                cycle_repetitions = (
                    missing_rocks // found_cycle.rocks_dropped - 1
                )  # 1 less repetition to avoid overshooting
                print(
                    f"Applying cycle: current dropped blocks: {blocks_dropped}. "
                    f"Need {missing_rocks:,} rocks to drop -> {cycle_repetitions=:,}"
                )
                blocks_dropped += cycle_repetitions * found_cycle.rocks_dropped
                cave_extra_height = cycle_repetitions * found_cycle.height
                print(
                    f"cycle applied: current dropped blocks: {blocks_dropped:,}. "
                    f"Old height {cave.height:,}. Gained extra height {cave_extra_height:,}"
                )
                cycle_applied = True

            if not found_cycle and cave.height >= height_to_start_searching_for_cycles:
                print(f"Got {len(tetris_cycle)} possible cycles")
                for (rock_type, wind_idx), cave_snapshots in tetris_cycle.items():
                    if len(cave_snapshots) < 5:  # min repetitions
                        continue
                    diffs_heights = {p[1] - p[0] for p in pairwise(h.height for h in cave_snapshots)}
                    diffs_blocks = {p[1] - p[0] for p in pairwise(h.rocks_dropped for h in cave_snapshots)}
                    all_the_same = all(p[1] == p[0] for p in pairwise(h.cave_state for h in cave_snapshots))
                    if len(diffs_heights) != 1 or len(diffs_blocks) != 1:
                        print(f"Found strange cycle: {rock_type} at wind {wind_idx}: {diffs_heights=}, {diffs_blocks=}")
                    print(f"Unique height differences: {diffs_heights}")
                    print([snapshot.height for snapshot in cave_snapshots])
                    print(f"Unique block count differences: {diffs_blocks} ({len(cave_snapshots)} total)")
                    print([snapshot.rocks_dropped for snapshot in cave_snapshots])
                    if all_the_same and len(diffs_heights) == 1 and len(diffs_blocks) == 1:
                        print(
                            f"All cave snapshots are the same!! {rock_type} at wind {wind_idx} ({len(cave_snapshots)} repetitions)"
                        )
                        found_cycle = Cycle(rock_type, wind_idx, diffs_heights.pop(), diffs_blocks.pop())
                        print("\n".join("".join(foo) for foo in reversed(cave_snapshots[0].cave_state)))
                        tetris_cycle.clear()
                        break
    print(f"{blocks_dropped=}")
    print(f"{cave.height=:,} + {cave_extra_height=:,} = {cave.height + cave_extra_height:,}")
    return cave.height + cave_extra_height


def part_1():
    MAX_ROCKS = 2022
    winds = load_data()
    final_height = tetris(winds, MAX_ROCKS)
    print(f"part 1 result: {final_height}")


def part_2():
    MAX_ROCKS = 1_000_000_000_000
    HEIGHT_TO_START_SEARCHING_FOR_CYCLES = 683 if TEST_DATA else 23_567
    winds = load_data()
    final_height = tetris2(winds, MAX_ROCKS, HEIGHT_TO_START_SEARCHING_FOR_CYCLES)
    print(f"part 2 result: {final_height}")


if __name__ == "__main__":
    print(f"default gc: {gc.get_threshold()}")
    gc.set_threshold(267_829, 38_342, 16_893)
    part_2()
