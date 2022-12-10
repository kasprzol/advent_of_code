import re


def part_1():
    x_register = 1
    program = []
    with open("input.txt") as indata:
        for line in indata:
            program.append(line)

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
            if m := addx.match(instruction):
                add_value = int(m[1])
                cpu_busy = True
            else:
                continue
        print(f"End of cycle {clock_cycle}, value of register is {x_register}, cpu {'not' if not cpu_busy else ''} is busy")
    print(sum(signal_strengths))


def part_2():
    with open("input.txt") as indata:
        for line in indata:
            ...


if __name__ == '__main__':
    part_1()
