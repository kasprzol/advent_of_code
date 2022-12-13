from tqdm import tqdm
import gc


def part_1():
    with open("input.txt") as indata:
        for line in indata:
            fish = [int(f) for f in line.split(",")]

    DAYS = 80
    fish_per_day = {}
    for day in tqdm(range(1, DAYS + 1), total=DAYS + 1, maxinterval=1):
        new_fish = []
        new_born = 0
        for one_fish in fish:
            one_fish -= 1
            if one_fish < 0:
                one_fish = 6
                new_born += 1
            new_fish.append(one_fish)
        new_fish.extend([8] * new_born)
        fish_per_day[day] = len(new_fish)
        print(f"{day=:2d}: {len(new_fish)}")
        fish = new_fish
    print(fish_per_day)


def part_2():
    with open("input.txt") as indata:
        for line in indata:
            fish = [int(f) for f in line.split(",")]

if __name__ == "__main__":
    part_1()
