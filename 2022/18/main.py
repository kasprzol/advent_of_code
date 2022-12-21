import gc
from collections import defaultdict

from rich import print

# from tqdm.rich import tqdm

from utils import Point3d

EMPTY = "."
LAVA = "\N{FULL BLOCK}"
TRAPPED_AIR = "\N{DARK SHADE}"
# MOVING_ROCK_FRAGMENT = "\N{DARK SHADE}"
# https://www.fileformat.info/info/unicode/block/block_elements/list.htm

TEST_DATA = False
if TEST_DATA:
    SPACE_SIZE = 20  # 7
else:
    SPACE_SIZE = 27


def load_lava() -> list[Point3d]:
    points = []
    with open("test_input.txt" if TEST_DATA else "input.txt") as indata:
        for line in indata:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            points.append(Point3d(*[int(coord) + 2 for coord in line.strip().split(",")]))
    return points


def part_1():
    lava = load_lava()
    space = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))
    for point in lava:
        space[point.x][point.y][point.z] = point

    exposed_sides = compute_surface(lava, space)

    print(f"part 1 result: {exposed_sides}")


def compute_surface(lava, space):
    exposed_sides = 0
    for point in lava:
        for side in [[0, 0, -1], [0, 0, 1], [0, -1, 0], [0, 1, 0], [-1, 0, 0], [1, 0, 0]]:
            if isinstance(space, dict):
                if (
                    point.x + side[0] not in space
                    or point.y + side[1] not in space[point.x]
                    or point.z + side[2] not in space[point.x][point.y]
                    or space[point.x + side[0]][point.y + side[1]][point.z + side[2]] is None
                ):
                    exposed_sides += 1
            elif (
                0 <= point.x + side[0] < SPACE_SIZE
                and 0 <= point.y + side[1] < SPACE_SIZE
                and 0 <= point.z + side[2] < SPACE_SIZE
            ) and space[point.x + side[0]][point.y + side[1]][point.z + side[2]] is None:
                exposed_sides += 1
    return exposed_sides


def compute_surface2(lava, space):
    exposed_sides = 0
    for point in lava:
        assert space[point.x][point.y][point.z]["content"] == "lava"
        for side in [[0, 0, -1], [0, 0, 1], [0, -1, 0], [0, 1, 0], [-1, 0, 0], [1, 0, 0]]:
            if (
                0 <= point.x + side[0] < SPACE_SIZE
                and 0 <= point.y + side[1] < SPACE_SIZE
                and 0 <= point.z + side[2] < SPACE_SIZE
            ) and space[point.x + side[0]][point.y + side[1]][point.z + side[2]]["content"] == "empty":
                exposed_sides += 1
    return exposed_sides


def part_2():
    lava = load_lava()

    space = [
        [[{"content": "empty", "color": "white"} for _x in range(SPACE_SIZE)] for _y in range(SPACE_SIZE)]
        for _z in range(SPACE_SIZE)
    ]
    for point in lava:
        space[point.x][point.y][point.z]["content"] = "lava"

    print_space2(space)

    queue = [Point3d(0, 0, 0)]
    while queue:
        p = queue.pop(0)
        if space[p.x][p.y][p.z]["color"] != "white":
            continue
        space[p.x][p.y][p.z]["color"] = "gray"
        for side in [[0, 0, -1], [0, 0, 1], [0, -1, 0], [0, 1, 0], [-1, 0, 0], [1, 0, 0]]:
            p2 = Point3d(p.x + side[0], p.y + side[1], p.z + side[2])
            # check that it's not outside
            if not ((0 <= p2.x < SPACE_SIZE) and (0 <= p2.y < SPACE_SIZE) and (0 <= p2.z < SPACE_SIZE)):
                continue

            # already checked
            if space[p2.x][p2.y][p2.z]["color"] != "white":
                continue

            if space[p2.x][p2.y][p2.z]["content"] == "empty":
                queue.append(p2)

        space[p.x][p.y][p.z]["color"] = "black"

    empty_spaces = find_empty_spaces(space)
    for p in empty_spaces:
        if space[p.x][p.y][p.z]["content"] == "empty" and space[p.x][p.y][p.z]["color"] == "white":
            space[p.x][p.y][p.z]["content"] = "trapped air"

    print_space2(space)
    exposed_sides = compute_surface2(lava, space)
    print(f"part 2 answer: {exposed_sides}")


def find_empty_spaces(space) -> set[Point3d]:
    empty_spaces: set[Point3d] = set()
    for x, x_plane in enumerate(space):
        for y, y_row in enumerate(x_plane):
            inside_droplet = False
            for z, cell in enumerate(y_row):
                if cell["content"] == "empty":
                    if inside_droplet:
                        empty_spaces.add(Point3d(x, y, z))
                        # print(f"Found empty space {x=}, {y=}, {z=}")
                else:
                    inside_droplet = True
    return empty_spaces


def print_space(space, outside=None):
    for x in range(SPACE_SIZE):
        space_slice = [["" for _ in range(SPACE_SIZE)] for __ in range(SPACE_SIZE)]
        print(f"{x=}")
        print(r"y\z 01234567890123456789012345")
        for y in range(SPACE_SIZE):
            for z in range(SPACE_SIZE):
                empty = "[yellow]:[/yellow]" if outside and Point3d(x, y, z) in outside else "."
                if isinstance(space[x][y][z], Point3d):
                    space_slice[y][z] = f"[red]{LAVA}[/red]"
                elif isinstance(space[x][y][z], str):
                    space_slice[y][z] = space[x][y][z]
                else:
                    space_slice[y][z] = empty
            print(f"{y:2}  " + "".join(space_slice[y]))


def print_space2(space):
    for x in range(SPACE_SIZE):
        space_slice = [["" for _ in range(SPACE_SIZE)] for __ in range(SPACE_SIZE)]
        print(f"{x=}")
        print(r"y\z 01234567890123456789012345")
        for y in range(SPACE_SIZE):
            for z in range(SPACE_SIZE):
                if space[x][y][z]["content"] == "empty":
                    if space[x][y][z]["color"] == "white":
                        empty = "[white].[/white]"
                    else:
                        empty = "[yellow]:[/yellow]"
                    space_slice[y][z] = empty
                elif space[x][y][z]["content"] == "lava":
                    space_slice[y][z] = f"[red]{LAVA}[/red]"
                elif space[x][y][z]["content"] == "trapped air":
                    space_slice[y][z] = f"[blue]{TRAPPED_AIR}[/blue]"
            print(f"{y:2}  " + "".join(space_slice[y]))


if __name__ == "__main__":
    print(f"default gc: {gc.get_threshold()}")
    gc.set_threshold(267_829, 38_342, 16_893)
    part_2()
