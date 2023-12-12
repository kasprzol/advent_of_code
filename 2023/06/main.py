import re
import dataclasses
from typing import NamedTuple
from collections.abc import Iterable, Sequence
import itertools
import tqdm

class Race(NamedTuple):
    time: int
    distance: int

def load_races() -> list[Race]:
    times = []
    distances = []
    for line in open("input.txt").readlines():
        line = line.strip()
        if line.startswith("Time:"):
            times = [int(x) for x in line.removeprefix("Time:").split()]
        elif line.startswith("Distance:"):
            distances = [int(x) for x in line.removeprefix("Distance:").split()]
    return [Race(t, d) for t,d in zip(times, distances)]

def part1():
    value = 1
    races = load_races()
    
    for race in tqdm.tqdm(races):
        how_long_to_press_to_win = []
        for i in tqdm.trange(1, race.time):
            if i * (race.time-i) > race.distance:
                how_long_to_press_to_win.append(i)
        print(f"Ways to win {race=}: {how_long_to_press_to_win}")
        value *= len(how_long_to_press_to_win)

    print(f"The value is {value}")

################################################################################

def part2():
    value = 1

    for line in open("input.txt").readlines():
        line = line.strip()
        if line.startswith("Time:"):
            time = int("".join(line.removeprefix("Time:").split()))
        elif line.startswith("Distance:"):
            distance = int( "".join(line.removeprefix("Distance:").split()))
    
    how_long_to_press_to_win = []
    for i in tqdm.trange(1, time):
        if i * (time-i) > distance:
            how_long_to_press_to_win.append(i)
    print(f"Ways to win race: {how_long_to_press_to_win}")
    value *= len(how_long_to_press_to_win)

    print(f"The value is {value}")

if __name__ == '__main__':
    part2()