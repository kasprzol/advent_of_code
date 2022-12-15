import gc
import re
from collections import defaultdict
from itertools import pairwise
from operator import attrgetter
import pickle
from dataclasses import dataclass
from typing import NamedTuple

from tqdm import tqdm

SENSOR = "S"
EMPTY = "."
BEACON = "B"
VISIBLE = "#"  # "\N{LIGHT SHADE}"
# NEW_SAND = "\N{FULL BLOCK}"
TARGET_COLUMN = 20_00_000


class Point(NamedTuple):
    x: int
    y: int


class Sensor(NamedTuple):
    position: Point
    beacon: Point
    distance: int

    # visible_area: list[complex]


@dataclass
class VisibilitySpan:
    length: int
    start: int
    stop: int


def print_cave(cave, cave_max_y):
    min_x = min(cave.keys())
    max_x = max(cave.keys())
    print()
    for y in range(cave_max_y + 1):
        row = [cave[x][y] for x in range(min_x, max_x + 1)]
        print(f"{y:2}", "".join(row))


def load_data():
    r = re.compile(r"Sensor at x=(?P<sx>-?\d+), y=(?P<sy>-?\d+): closest beacon is at x=(?P<bx>-?\d+), y=(?P<by>-?\d+)")
    sensors = []
    beacons = []
    cave = defaultdict(lambda: defaultdict(lambda: EMPTY))
    cave_min_x, cave_max_x, cave_max_y = 99999, 0, 0
    with open("input.txt") as indata:
        for line in indata:
            matches = r.match(line)
            sx, sy, bx, by = (
                int(matches["sx"]),
                int(matches["sy"]),
                int(matches["bx"]),
                int(matches["by"]),
            )
            beacon = Point(bx, by)
            beacons.append(beacon)
            sensor_pos = Point(sx, sy)
            sensors.append(Sensor(sensor_pos, beacon, distance(sensor_pos, beacon)))
            print(sensors[-1])
            cave[sx][sy] = SENSOR
            cave[bx][by] = BEACON
            cave_min_x = min((cave_min_x, sx, bx))
            cave_max_x = max((cave_max_x, sx, bx))
            cave_max_y = max((cave_max_y, sy, by))
    return sensors, beacons, cave, cave_min_x, cave_max_x, cave_max_y


def distance(p1: Point, p2: Point) -> int:
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)


def compute_visibility(sensors) -> defaultdict[int, list[VisibilitySpan]]:
    visibility_spans: defaultdict[int, list[VisibilitySpan]] = defaultdict(list)
    for sensor in tqdm(sensors, desc="sensors", leave=False):
        # we're really only interested in TARGET_COLUMN - this could be optimised to check only for that
        # if not (
        #     (sensor.position.y <= TARGET_COLUMN <= sensor.position.y + sensor.distance)
        #     or (sensor.position.y - sensor.distance <= TARGET_COLUMN <= sensor.position.y)
        # ):
        #     continue
        for distance_from_row in tqdm(range(sensor.distance + 1), desc="distance", leave=False):
            span_length = 2 * (sensor.distance - distance_from_row) + 1
            interesting_rows = {
                sensor.position.y - distance_from_row,
                sensor.position.y + distance_from_row,
            }
            if TARGET_COLUMN not in interesting_rows:
                continue
            for row in interesting_rows:
                new_span = VisibilitySpan(
                    span_length,
                    sensor.position.x - (sensor.distance - distance_from_row),
                    sensor.position.x + (sensor.distance - distance_from_row),
                )
                visibility_spans[row].append(new_span)
    # coalesce overlapping spans
    for row in tqdm(visibility_spans, desc="Coalesce"):
        row_modified = True
        while row_modified:
            row_modified = False
            visibility_spans[row].sort(key=attrgetter("start"))
            for span1, span2 in pairwise(visibility_spans[row]):
                if (span1.start <= span2.start <= span1.stop) or (span1.start <= span2.stop <= span1.stop):
                    span1.start = min(span1.start, span2.start)
                    span1.stop = max(span1.stop, span2.stop)
                    span1.length = span1.stop - span1.start + 1
                    visibility_spans[row].remove(span2)
                    row_modified = True
                    break
    return visibility_spans


def part_1():
    sensors, beacons, cave, cave_min_x, cave_max_x, cave_max_y = load_data()
    # print_cave(cave, cave_max_y)
    visibility_spans = compute_visibility(sensors)
    # with open("visibility.pickle", "wb") as dump:
    #     pickle.dump((sensors, beacons, cave, cave_min_x, cave_max_x, cave_max_y), dump)
    # print_cave(cave, cave_max_y)
    occupied_x = [x for x in cave if TARGET_COLUMN in cave[x]]
    visibility_count = 0
    for span in tqdm(visibility_spans[TARGET_COLUMN], desc="calculating visibility"):
        visibility_count += span.length
        for x in occupied_x:
            if span.start <= x <= span.stop:
                visibility_count -= 1
    print(f"{visibility_count=}")


def part_2():
    ...


if __name__ == "__main__":
    print(f"default gc: {gc.get_threshold()}")
    gc.set_threshold(567_829, 48_342, 6_893)
    part_1()
