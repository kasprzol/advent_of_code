from tqdm import tqdm
import gc


def part_1():
    with open("input.txt") as indata:
        for line in indata:
            crabpos = [int(f) for f in line.split(",")]

    min_crab = min(crabpos)
    max_crab = max(crabpos)
    min_fuel_cost = 999999_999999**3
    for pos in range(min_crab, max_crab + 1):
        total_cost = 0
        for crab in crabpos:
            cost = crab - pos
            if cost < 0:
                cost *= -1
            total_cost += cost
        if total_cost < min_fuel_cost:
            min_fuel_cost = total_cost
    print(min_fuel_cost)


def part_2():
    with open("input.txt") as indata:
        for line in indata:
            crabpos = [int(f) for f in line.split(",")]

    min_crab = min(crabpos)
    max_crab = max(crabpos)
    move_cost_per_distance = {0: 0, 1: 1}
    for i in range(2, max_crab - min_crab + 1):
        move_cost_per_distance[i] = move_cost_per_distance[i - 1] + i
    min_fuel_cost = 999999_999999**3
    for pos in range(min_crab, max_crab + 1):
        total_cost = 0
        for crab in crabpos:
            distance = abs(crab - pos)
            total_cost += move_cost_per_distance[distance]
        if total_cost < min_fuel_cost:
            min_fuel_cost = total_cost
    print(min_fuel_cost)


if __name__ == "__main__":
    part_2()
