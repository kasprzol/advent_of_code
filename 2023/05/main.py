import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence
import itertools
import tqdm


class RangeMap(NamedTuple):
    source: int
    dest: int
    length: int


@dataclasses.dataclass
class Mapping:
    ranges: list[RangeMap]
    source_type: str
    dest_type: str

    def __contains__(self, number: int) -> bool:
        for range in self.ranges:
            if range.source <= number <= range.source + range.length:
                return True
        return False

    def __getitem__(self, idx: int) -> bool:
        for range in self.ranges:
            if range.source <= idx <= range.source + range.length:
                dest_idx = idx - range.source
                return range.dest + dest_idx
        raise KeyError(f"{idx=} not found in {self.ranges}")


def get_location_from_seed(seed: int, mappings, type_mappings: dict[str, str]) -> int:
    current_type = "seed"
    current_value = seed
    while current_type != "location":
        if current_value in mappings[current_type]:
            new_value = mappings[current_type][current_value]
        else:
            new_value = current_value
        current_value = new_value
        current_type = type_mappings[current_type]
    return current_value


def part1():
    value = 0
    seeds = []
    current_ranges = []
    type_mappings = {}
    mappings = {}

    def commit_mapping():
        nonlocal current_ranges
        if current_ranges:
            m = Mapping(ranges=current_ranges, source_type=mapping_from, dest_type=mapping_to)
            mappings[mapping_from] = m
            current_ranges = []

    for line in open("input.txt").readlines():
        line = line.strip()
        if line.startswith("seeds:"):
            seeds = [int(x) for x in line.split(":")[1].split()]
        elif ":" in line:
            mapping_from, mapping_to = line.split()[0].split("-to-")
            type_mappings[mapping_from] = mapping_to
        elif line:  # not empty line - a range
            dest_start, source_start, length = [int(x) for x in line.split()]
            r = RangeMap(source=source_start, dest=dest_start, length=length)
            current_ranges.append(r)
        else:  # empty line
            commit_mapping()

    commit_mapping()
    lowest_location = 2**2048
    for seed in seeds:
        if (
            seed_location := get_location_from_seed(seed, mappings=mappings, type_mappings=type_mappings)
        ) < lowest_location:
            lowest_location = seed_location

    print(f"The value is {lowest_location}")


################################################################################


def range_intersection(range_a: tuple[int, int], range_b: tuple[int, int]):
    """Return the result of intersection of 2 ranges of numbers.

    The ranges are interpreted as (start, length).

    Returns three values:
    - a range before the intersection (or None)
    - the intersection (or None)
    - the range after the intersection (or None)
    """
    if range_a[0] > range_b[0]:
        range_a, range_b = range_b, range_a

    range_a_start = range_a[0]
    range_b_start = range_b[0]
    range_a_end = range_a[0] + range_a[1] - 1
    range_b_end = range_b[0] + range_b[1] - 1

    def start_end_to_start_length(start: int, end: int):
        return start, end - start + 1

    intersection_start = max(range_a_start, range_b_start)
    intersection_end = min(range_a_end, range_b_end)

    if intersection_start > intersection_end:
        return range_a, None, range_b

    intersection = start_end_to_start_length(intersection_start, intersection_end)

    if range_a_start < intersection_start:
        before_start = range_a_start
        before_end = intersection_start - 1
        assert before_start <= before_end
        before = start_end_to_start_length(before_start, before_end)
    else:
        before = None

    if intersection_end < range_a_end or intersection_end < range_b_end:
        after_start = intersection_end + 1
        after_end = max(range_a_end, range_b_end)
        after = start_end_to_start_length(after_start, after_end)
    else:
        after = None

    return before, intersection, after


def part2():
    value = 0
    seeds = []
    current_ranges = []
    type_mappings = {}
    mappings: dict[str, Mapping] = {}

    def commit_mapping():
        nonlocal current_ranges
        if current_ranges:
            m = Mapping(ranges=current_ranges, source_type=mapping_from, dest_type=mapping_to)
            mappings[mapping_from] = m
            current_ranges = []

    for line in open("input.txt").readlines():
        line = line.strip()
        if line.startswith("seeds:"):
            seeds = [int(x) for x in line.split(":")[1].split()]
        elif ":" in line:
            mapping_from, mapping_to = line.split()[0].split("-to-")
            type_mappings[mapping_from] = mapping_to
        elif line:  # not empty line - a range
            dest_start, source_start, length = [int(x) for x in line.split()]
            r = RangeMap(source=source_start, dest=dest_start, length=length)
            current_ranges.append(r)
        else:  # empty line
            commit_mapping()

    commit_mapping()
    lowest_location = 2**2048

    for seed_start, length in tqdm.tqdm(itertools.batched(seeds, 2)):
        current_type = "seed"
        current_ranges = [(seed_start, length)]
        # target_type = type_mappings[current_type]
        while current_type != "location":
            mapped_ranges = []
            unmapped_ranges = []
            for target_range in mappings[current_type].ranges:
                for current_range in current_ranges:
                    # TODO: mając mapowania z jednego typu na drugi, może dojść do sytuacji, gdy tylko część zakresu zostanie zmapowana (intersection) a pozostałe trafią do before lub after.
                    # ale nawet wtedy mogą być zmapowane przez inne mapowania tego typu. trzeba sprawdzić wszystkie możliwości. a to co zostanie, jest przenoszone bezpośrednio (source=dest)
                    before, intersection, after = range_intersection(
                        current_range, (target_range.source, target_range.length)
                    )
                    if before:
                        new_ranges.append(before)
                    if after:
                        new_ranges.append(after)

            current_ranges = new_ranges
            current_type = type_mappings[current_type]
        if (new_lowest := min(current_ranges, key=lambda x: x[0])) < lowest_location:
            lowest_location = new_lowest

    print(f"The value is {lowest_location}")


if __name__ == "__main__":
    part2()
