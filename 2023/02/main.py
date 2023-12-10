import re
from collections.abc import Iterable




def part1():
    total_max = {"red": 12, "green" : 13, "blue": 14}
    r_game_id = re.compile("Game (?P<id>\\d+):")
    r_cubes = re.compile("(?P<count>\\d+) (?P<color>(?:red)|(?:green)|(?:blue))")
    value = 0
    for line in open("input.txt"):
        line = line.strip()
        game_id = r_game_id.match(line)
        subsets = line.split(":")[1].split(";")
        game_max = {"red": 0, "green": 0, "blue":0}
        for subset in subsets:
            for color in subset.split(","):
                match = r_cubes.match(color.strip())
                if (count := int(match["count"])) > game_max[match["color"]]:
                    game_max[match["color"]] = count
        valid = True
        for color in game_max:
            if game_max[color] > total_max[color]:
                valid = False
                break
        if valid:
            value += int(game_id["id"])


    print(f"The value is {value}")


def part2():
    r_game_id = re.compile("Game (?P<id>\\d+):")
    r_cubes = re.compile("(?P<count>\\d+) (?P<color>(?:red)|(?:green)|(?:blue))")
    value = 0
    for line in open("input.txt"):
        line = line.strip()
        subsets = line.split(":")[1].split(";")
        game_max = {"red": 0, "green": 0, "blue":0}
        for subset in subsets:
            for color in subset.split(","):
                match = r_cubes.match(color.strip())
                if (count := int(match["count"])) > game_max[match["color"]]:
                    game_max[match["color"]] = count
        power = game_max["red"] * game_max["green"] * game_max["blue"]
        value += power


    print(f"The value is {value}")



if __name__ == '__main__':
    part2()
