
def part_1():
    with open("input.txt") as indata:
        prev = None
        count_increases = 0
        for depth in indata:
            depth = int(depth)
            if prev and depth > prev:
                count_increases += 1
            prev = depth
    print(count_increases)

def part_2():
    with open("input.txt") as indata:
        count_increases = 0
        depth_data = [int(depth) for depth in indata]
        for i in range(0, len(depth_data) - 2):
            sliding_window1 = depth_data[i:i+3]
            sliding_window2 = depth_data[i+1:i+4]
            sum1 = sum(sliding_window1)
            sum2 = sum(sliding_window2)
            print(f"{sliding_window1}, {sliding_window2}, {sum1}, {sum2}")
            if sum2 > sum1:
                count_increases += 1

    print(count_increases)


if __name__ == '__main__':
    part_2()