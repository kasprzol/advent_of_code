import re


def part_1():
    x_register = 1
    program = []
    with open("input.txt") as indata:
        program.extend(iter(indata))
    cpu_busy = False
    addx = re.compile(r"addx (-?\d+)")
    noop = re.compile("noop")
    add_value = 0
    signal_strengths = []
    for clock_cycle in range(1, 222):
        if clock_cycle in (20, 60, 100, 140, 180, 220):
            signal_strengths.append(x_register * clock_cycle)
        if cpu_busy:
            cpu_busy = False
            x_register += add_value
            continue
        else:
            instruction = program.pop(0)
            if not (m := addx.match(instruction)):
                continue
            add_value = int(m[1])
            cpu_busy = True

    print(sum(signal_strengths))


def part_2():
    x_register = 1
    program = []
    with open("input.txt") as indata:
        program.extend(iter(indata))
    cpu_busy = False
    addx = re.compile(r"addx (-?\d+)")
    noop = re.compile("noop")
    add_value = 0
    screen = [["."] * 40 for _ in range(6)]
    for clock_cycle in range(1, 240):
        current_pixel = (clock_cycle - 1) % 40
        if current_pixel in (x_register - 1, x_register, x_register + 1):
            current_row = clock_cycle // 40
            screen[current_row][current_pixel] = "#"
        if cpu_busy:
            cpu_busy = False
            x_register += add_value
            continue
        else:
            instruction = program.pop(0)
            if not (m := addx.match(instruction)):
                continue
            add_value = int(m[1])
            cpu_busy = True

    for row in screen:
        print("".join(row))


if __name__ == '__main__':
    part_2()
