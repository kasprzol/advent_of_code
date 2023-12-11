import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence


class Range(NamedTuple):
    source: int
    dest: int
    length: int

@dataclasses.dataclass
class Mapping:
    ranges: list[Range]
    source_type: str
    dest_type: str


    def __contains__(self, number:int) -> bool:
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
            r = Range(source=source_start, dest=dest_start, length=length)
            current_ranges.append(r)
        else: # empty line
            commit_mapping()

    commit_mapping()
    lowest_location = 2 ** 2048
    for seed in seeds:
        if (seed_location := get_location_from_seed(seed, mappings=mappings, type_mappings=type_mappings)) < lowest_location:
            lowest_location = seed_location

    print(f"The value is {lowest_location}")

################################################################################

def part2():
    value = 0

    print(f"The value is {value}")


if __name__ == '__main__':
    part1()
