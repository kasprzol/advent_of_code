
def part_1():
    depth = 0
    horizontal = 0
    with open("input.txt") as indata:
        for line in indata:
            command, value = line.split()
            value = int(value)
            match command:
                case "forward":
                    horizontal += value
                case "up":
                    depth -= value
                case "down":
                    depth += value
            print(f"{horizontal}, {depth}")
    print(horizontal * depth)

def part_2():
    depth = 0
    horizontal = 0
    aim = 0
    with open("input.txt") as indata:
        for line in indata:
            command, value = line.split()
            value = int(value)
            match command:
                case "forward":
                    horizontal += value
                    depth += value * aim
                case "up":
                    aim -= value
                case "down":
                    aim += value
            print(f"{horizontal}, {depth}, {aim}")
    print(horizontal * depth)

if __name__ == '__main__':
    part_2()
