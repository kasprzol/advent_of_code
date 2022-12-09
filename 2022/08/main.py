from functools import reduce
from operator import mul


def trees_in_column(forest: list[list[int]], column: int, start: int = 0, end: int = -1):
    for row_of_trees in forest[start:end]:
        # print(f"yielding {row_of_trees[column]} ({column=}, {start=}, {end=}")
        yield row_of_trees[column]


def part_1():
    forest = []
    with open("input.txt") as indata:
        forest.extend(list(line.strip()) for line in indata)
    R = len(forest)
    C = len(forest[0])
    # the edge is always visible
    sum_visible = 2 * len(forest) + 2 * (len(forest[0]) - 2)
    for r, row in enumerate(forest[1:-1], 1):
        for c, tree in enumerate(row[1:-1], 1):
            if all(other_tree < tree for other_tree in row[:c]) or all(other_tree < tree for other_tree in row[c + 1:]):
                sum_visible += 1
                continue
            ###
            trees_before = row[:c]
            trees_after = row[c + 1:]
            trees_above = list(trees_in_column(forest, c, 0, r))
            trees_below = list(trees_in_column(forest, c, r + 1, C))
            print(
                f"{r=},{c=} {tree=}, before={trees_before}, after={trees_after}, above={trees_above}, below={trees_below}")
            ###
            if all(other_tree < tree for other_tree in trees_in_column(forest, c, 0, r)) or all(
                    other_tree < tree for other_tree in trees_in_column(forest, c, r + 1, C)):
                sum_visible += 1
                continue
    print(sum_visible)


def part_2():
    forest = []
    with open("input.txt") as indata:
        forest.extend(list(line.strip()) for line in indata)
    R = len(forest)
    C = len(forest[0])
    # the edge is always visible
    highest_score = 0
    for r, row in enumerate(forest[1:-1], 1):
        for c, tree in enumerate(row[1:-1], 1):
            partial_scores = []

            one_direction_score = 0
            for other_tree_idx in range(c - 1, -1, -1):
                one_direction_score += 1
                if row[other_tree_idx] >= tree:
                    break
            partial_scores.append(one_direction_score)

            one_direction_score = 0
            for other_tree in row[c + 1:]:
                one_direction_score += 1
                if other_tree >= tree:
                    break
            partial_scores.append(one_direction_score)

            one_direction_score = 0
            for other_row_idx in range(r - 1, -1, -1):
                one_direction_score += 1
                if forest[other_row_idx][c] >= tree:
                    break
            partial_scores.append(one_direction_score)

            one_direction_score = 0
            for other_row in forest[r + 1:]:
                one_direction_score += 1
                if other_row[c] >= tree:
                    break
            partial_scores.append(one_direction_score)

            print(partial_scores)
            if (score := reduce(mul, partial_scores, 1)) > highest_score:
                highest_score = score
    print(highest_score)


if __name__ == '__main__':
    part_2()
