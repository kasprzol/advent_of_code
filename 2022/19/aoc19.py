import argparse
import contextlib
import functools
import re
import time
import typing
from io import TextIOWrapper

from rich import print
from tqdm import tqdm

VERBOSE = False


class Cost(typing.NamedTuple):
    ore: int
    clay: int
    obsidian: int


class Resources(typing.NamedTuple):
    ore: int
    clay: int
    obsidian: int
    geodes: int


class Blueprint(typing.NamedTuple):
    number: int
    ore_robot_cost: Cost
    clay_robot_cost: Cost
    obsidian_robot_cost: Cost
    geode_robot_cost: Cost


class Robots(typing.NamedTuple):
    ore: int
    clay: int
    obsidian: int
    geode: int


def load_input(indata: TextIOWrapper):
    blueprints = []
    # blueprint_re = re.compile(r"Blueprint (?P<id>\d+): Each ore robot costs (?P<ore_robot_cost_ore>\d+) ore. Each clay robot costs (?P<clay_robot_ore_cost>\d+) ore. Each obsidian robot costs (?P<obsidian_robot_cost>\d+) ore and 15 clay. Each geode robot costs 3 ore and 8 obsidian.")
    int_re = re.compile(r"\d+")

    for row_idx, line in enumerate(indata):
        line = line.strip().split("#")[0]
        if not line:
            continue
        ints = [int(x) for x in int_re.findall(line)]
        ore_robot_cost = Cost(ore=ints[1], clay=0, obsidian=0)
        clay_robot_cost = Cost(ore=ints[2], clay=0, obsidian=0)
        obsidian_robot_cost = Cost(ore=ints[3], clay=ints[4], obsidian=0)
        geode_robot_cost = Cost(ore=ints[5], clay=0, obsidian=ints[6])
        blueprints.append(
            Blueprint(
                number=ints[0],
                ore_robot_cost=ore_robot_cost,
                clay_robot_cost=clay_robot_cost,
                obsidian_robot_cost=obsidian_robot_cost,
                geode_robot_cost=geode_robot_cost,
            )
        )

    return blueprints


BLUEPRINT: Blueprint = None
TOTAL_MINUTES_PART1 = 24


@functools.lru_cache(maxsize=90_000_000)
def part1_worker_helper(robots: Robots, resources: Resources, minutes_left: int):
    if VERBOSE:
        print(f"minutes_left: {minutes_left}\t{robots}\t{resources}")

    # if ((ci := part1_worker_helper.cache_info()).hits + ci.misses) % 200_000 == 0:
    #     print(ci, f"{ci.hits / (ci.hits+ci.misses):.2%}")
    if minutes_left == 0:
        return resources.geodes, tuple()
    geodes_when_constructed_ore_robot = 0, tuple()
    geodes_when_constructed_clay_robot = 0, tuple()
    geodes_when_constructed_obsidian_robot = 0, tuple()
    geodes_when_constructed_geode_robot = 0, tuple()
    geodes_when_no_robots_constructed = 0, tuple()
    if resources.obsidian >= BLUEPRINT.geode_robot_cost.obsidian and resources.ore >= BLUEPRINT.geode_robot_cost.ore:
        new_resources = Resources(
            ore=resources.ore - BLUEPRINT.geode_robot_cost.ore + robots.ore,
            clay=resources.clay + robots.clay,
            obsidian=resources.obsidian - BLUEPRINT.geode_robot_cost.obsidian + robots.obsidian,
            geodes=resources.geodes + robots.geode,
        )
        res = part1_worker_helper(robots._replace(geode=robots.geode + 1), new_resources, minutes_left - 1)
        geodes_when_constructed_geode_robot = res[0], ((TOTAL_MINUTES_PART1 - minutes_left, "geode"), *res[1])
    if (
        resources.clay >= BLUEPRINT.obsidian_robot_cost.clay
        and resources.ore >= BLUEPRINT.obsidian_robot_cost.ore
        and robots.obsidian
        < BLUEPRINT.geode_robot_cost.obsidian  # don't build more obsidian robots than the cost of a geode robot
    ):
        new_resources = Resources(
            ore=resources.ore - BLUEPRINT.obsidian_robot_cost.ore + robots.ore,
            clay=resources.clay - BLUEPRINT.obsidian_robot_cost.clay + robots.clay,
            obsidian=resources.obsidian + robots.obsidian,
            geodes=resources.geodes + robots.geode,
        )
        res = part1_worker_helper(robots._replace(obsidian=robots.obsidian + 1), new_resources, minutes_left - 1)
        geodes_when_constructed_obsidian_robot = res[0], ((TOTAL_MINUTES_PART1 - minutes_left, "obsidian"), *res[1])
    # don't build more clay robots than obsidian robot cost.
    if resources.ore >= BLUEPRINT.clay_robot_cost.ore and robots.clay < BLUEPRINT.obsidian_robot_cost.clay:
        new_resources = Resources(
            ore=resources.ore - BLUEPRINT.clay_robot_cost.ore + robots.ore,
            clay=resources.clay + robots.clay,
            obsidian=resources.obsidian + robots.obsidian,
            geodes=resources.geodes + robots.geode,
        )
        res = part1_worker_helper(robots._replace(clay=robots.clay + 1), new_resources, minutes_left - 1)
        geodes_when_constructed_clay_robot = res[0], ((TOTAL_MINUTES_PART1 - minutes_left, "clay"), *res[1])
    if resources.ore >= BLUEPRINT.ore_robot_cost.ore and robots.ore < max(
        BLUEPRINT.ore_robot_cost.ore,
        BLUEPRINT.clay_robot_cost.ore,
        BLUEPRINT.obsidian_robot_cost.ore,
        BLUEPRINT.geode_robot_cost.ore,
    ):
        new_resources = Resources(
            ore=resources.ore - BLUEPRINT.ore_robot_cost.ore + robots.ore,
            clay=resources.clay + robots.clay,
            obsidian=resources.obsidian + robots.obsidian,
            geodes=resources.geodes + robots.geode,
        )
        res = part1_worker_helper(robots._replace(ore=robots.ore + 1), new_resources, minutes_left - 1)
        geodes_when_constructed_ore_robot = res[0], ((TOTAL_MINUTES_PART1 - minutes_left, "ore"), *res[1])

    new_resources = Resources(
        ore=resources.ore + robots.ore,
        clay=resources.clay + robots.clay,
        obsidian=resources.obsidian + robots.obsidian,
        geodes=resources.geodes + robots.geode,
    )
    geodes_when_no_robots_constructed = part1_worker_helper(robots, new_resources, minutes_left - 1)

    return max(
        geodes_when_constructed_ore_robot,
        geodes_when_constructed_clay_robot,
        geodes_when_constructed_obsidian_robot,
        geodes_when_constructed_geode_robot,
        geodes_when_no_robots_constructed,
    )


def part1_work(blueprint: Blueprint):
    total_minutes = 24
    part1_worker_helper.cache_clear()
    global BLUEPRINT
    BLUEPRINT = blueprint
    res = part1_worker_helper(Robots(1, 0, 0, 0), Resources(0, 0, 0, 0), total_minutes)
    print(res[1])
    return res[0]


def part1(input_file: TextIOWrapper):
    blueprints = load_input(input_file)
    if VERBOSE:
        print(blueprints)
    result = 0
    part1_start = time.monotonic()
    for bp in blueprints:
        bp_started_at = time.monotonic()
        number_of_geodes = part1_work(bp)
        bp_finish = time.monotonic()
        quality_level = bp.number * number_of_geodes
        print(f"{bp.number} * {number_of_geodes} = {quality_level}. Took {bp_finish - bp_started_at:.2f} seconds.")
        result += quality_level
    part1_finish = time.monotonic()
    print(
        f"Part 1: {result:,}. Took {part1_finish - part1_start:.2f} seconds ({(part1_finish-part1_start)/60:.2f} minutes)."
    )
    print(f"Part 1: {result:,}")


def part2_work(blueprint: Blueprint):
    total_minutes = 32
    part1_worker_helper.cache_clear()
    global BLUEPRINT
    BLUEPRINT = blueprint
    res = part1_worker_helper(Robots(1, 0, 0, 0), Resources(0, 0, 0, 0), total_minutes)
    print(res[1])
    return res[0]


def part2(input_file: TextIOWrapper):
    blueprints = load_input(input_file)
    blueprints = blueprints[:3]
    if VERBOSE:
        print(blueprints)
    result = 1
    part1_start = time.monotonic()
    for bp in blueprints:
        bp_started_at = time.monotonic()
        number_of_geodes = part2_work(bp)
        bp_finish = time.monotonic()
        print(f"{bp.number}: {number_of_geodes}. Took {bp_finish - bp_started_at:.2f} seconds.")
        result *= number_of_geodes
    part1_finish = time.monotonic()
    print(
        f"Part 2: {result:,}. Took {part1_finish - part1_start:.2f} seconds ({(part1_finish-part1_start)/60:.2f} minutes)."
    )
    print(f"Part 2: {result:,}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", type=int, choices=[1, 2])
    parser.add_argument("input", type=argparse.FileType("r"), default="test_input.txt")
    parser.add_argument("-v", "--verbose", action="store_true")
    arguments = parser.parse_args()
    global VERBOSE
    VERBOSE = arguments.verbose
    if arguments.part == 1:
        part1(arguments.input)
    elif arguments.part == 2:
        part2(arguments.input)


if __name__ == "__main__":
    main()
