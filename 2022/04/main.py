def part_1():
    def fully_contained(a, b):
        return (a[0] >= b[0] and a[1] <= b[1]) or (b[0] >= a[0] and b[1] <= a[1])

    with open("input.txt") as indata:
        fully_contained_sections = 0
        for line in indata:
            sections_specs = line.split(",")
            for i in range(len(sections_specs)):
                sections_specs[i] = sections_specs[i].split("-")
                sections_specs[i][0] = int(sections_specs[i][0])
                sections_specs[i][1] = int(sections_specs[i][1])
            if fully_contained(sections_specs[0], sections_specs[1]):
                fully_contained_sections +=1

    print(fully_contained_sections)


def part_2():
    def partial_overlap(a, b):
        return (b[0] <= a[0] <= b[1]) or (b[0] <= a[1] <= b[1]) or (a[0] <= b[0] <= a[1]) or (a[0] <= b[1] <= a[1])

    with open("input.txt") as indata:
        partially_contained_sections = 0
        for line in indata:
            sections_specs = line.split(",")
            for i in range(len(sections_specs)):
                sections_specs[i] = sections_specs[i].split("-")
                sections_specs[i][0] = int(sections_specs[i][0])
                sections_specs[i][1] = int(sections_specs[i][1])
            if partial_overlap(sections_specs[0], sections_specs[1]):
                partially_contained_sections +=1

    print(partially_contained_sections)


if __name__ == '__main__':
    part_2()
