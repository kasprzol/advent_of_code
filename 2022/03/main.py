from collections import Counter


def part_2():
    priorities = {
        **{chr(letter): prio for prio, letter in enumerate(range(ord("a"), ord("z") + 1), start=1)},
        **{chr(letter): prio for prio, letter in enumerate(range(ord("A"), ord("Z") + 1), start=27)}
    }
    with open("input.txt") as indata:
        sum_prio = 0
        group_count = 0
        group_items = Counter()

        for rucksack in indata:
            group_items.update(set(rucksack.strip()))
            group_count += 1
            if group_count % 3 == 0:
                sum_prio += priorities[group_items.most_common(1)[0][0]]
                group_items.clear()

    print(sum_prio)


def part_1():
    priorities = {
        **{chr(letter): prio for prio, letter in enumerate(range(ord("a"), ord("z") + 1), start=1)},
        **{chr(letter): prio for prio, letter in enumerate(range(ord("A"), ord("Z") + 1), start=27)}
    }
    with open("input.txt") as indata:
        sum_prio = 0
        for rucksack in indata:
            l = len(rucksack) // 2
            compartments = rucksack[:l], rucksack[l:]
            left, right = set(compartments[0]), set(compartments[1])
            common = left & right
            common = list(common)
            print(common, [priorities[c] for c in common])
            for c in common:
                sum_prio += priorities[c]

    print(sum_prio)


if __name__ == '__main__':
    part_2()
