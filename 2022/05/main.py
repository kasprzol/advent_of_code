import re


def part_1():
    stacks = []
    for i in range(9):
        stacks.append(list())
    with open("input.txt") as indata:
        # input stacks
        for line in indata:
            if "[" not in line:
                break
            for i in range(9):
                item = line[i * 4: (i + 1) * 4][1]
                if item.strip():
                    stacks[i].insert(0, item)

        r = re.compile(r"move (\d+) from (\d+) to (\d+)")
        # operations
        for line in indata:
            if line.strip() == "":
                continue
            matches = r.match(line)
            amount = int(matches[1])
            frm = int(matches[2]) - 1
            to = int(matches[3]) - 1
            for i in range(amount):
                try:
                    item = stacks[frm].pop()
                except IndexError as e:
                    print(f"error poping from empty stack {frm} ({i}/{amount})")
                stacks[to].append(item)

    tops = [stacks[i].pop() for i in range(9)]
    print(tops)


def part_2():
    stacks = []
    for i in range(9):
        stacks.append(list())
    with open("input.txt") as indata:
        # input stacks
        for line in indata:
            if "[" not in line:
                break
            for i in range(9):
                item = line[i * 4: (i + 1) * 4][1]
                if item.strip():
                    stacks[i].insert(0, item)

        r = re.compile(r"move (\d+) from (\d+) to (\d+)")
        # operations
        for line in indata:
            if line.strip() == "":
                continue
            matches = r.match(line)
            amount = int(matches[1])
            frm = int(matches[2]) - 1
            to = int(matches[3]) - 1

            items = stacks[frm][-amount:]
            del stacks[frm][- amount:]
            stacks[to].extend(items)

    tops = [stacks[i].pop() for i in range(9)]
    print(tops)


if __name__ == '__main__':
    part_2()
