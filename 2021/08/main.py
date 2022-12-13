from tqdm import tqdm
import gc


def decode_segments(puzzle):
    segments = {
        1: frozenset(puzzle[0][0]),
        4: frozenset(puzzle[0][2]),
        7: frozenset(puzzle[0][1]),
        8: frozenset(puzzle[0][9]),
    }

    candidates_2_3_5 = {frozenset(puzzle[0][3]), frozenset(puzzle[0][4]), frozenset(puzzle[0][5])}
    candidates_0_6_9 = {frozenset(puzzle[0][6]), frozenset(puzzle[0][7]), frozenset(puzzle[0][8])}

    segments["a"] = segments[7] - segments[1]

    # 2 & 3 have one different segment - one of 1's segments (f)
    # 2 & 5 have one different segment - one of 1's segments (f)
    # 6 is 5 with one extra segment (e)
    # in the 0, 6, 9 set the one without segment c (one of 1's) is 6
    for candidate_6 in candidates_0_6_9:
        if not segments[1].issubset(candidate_6):
            segments[6] = candidate_6
            candidates_0_9 = candidates_0_6_9 - {candidate_6}
            break
    else:
        assert False, "not reached"
    for candidate_5 in candidates_2_3_5:
        if candidate_5 <= segments[6]:
            segments[5] = candidate_5
            candidates_2_3 = candidates_2_3_5 - {candidate_5}
            break
    else:
        assert False, "not reached"
    segments["e"] = list(segments[6] - segments[5])[0]
    for candidate_0 in candidates_0_9:
        if segments["e"] in candidate_0:
            segments[0] = candidate_0
            segments[9] = (candidates_0_9 - {candidate_0}).pop()
            break
    else:
        assert False, "not reached"
    segments["d"] = list(segments[9] - segments[0])[0]
    for candidate_2 in candidates_2_3:
        if candidate_2.intersection(segments["e"]):
            segments[2] = candidate_2
            ####
            segments[3] = (candidates_2_3 - {candidate_2}).pop()
            segments["f"] = list(segments[3] - segments[2])[0]
            break
    else:
        assert False, "not reached"
    # when I have 9 i can do segments["b"] = segments[9] - segments[3]
    segments["b"] = list(segments[9] - segments[3])[0]
    segments["g"] = list(segments[9] - segments[7] - {segments["b"]} - {segments["d"]})[0]
    segments["a"] = list(segments[9] - segments[4] - {segments["g"]})[0]
    segments["c"] = list(segments[2] - segments[5])[0]
    assert (
        segments["a"]
        != segments["b"]
        != segments["c"]
        != segments["d"]
        != segments["e"]
        != segments["f"]
        != segments["g"]
    )
    return segments


def part_1():
    puzzles = []
    with open("input.txt") as indata:
        for line in indata:
            observation, reading = line.strip().split("|")
            observation = observation.split()
            observation.sort(key=len)
            reading = reading.split()
            puzzles.append((observation, reading))

    num_times_1_4_7_8 = 0
    for puzzle in puzzles:
        segments = decode_segments(puzzle)
        # In the output values, how many times do digits 1, 4, 7, or 8 appear?
        for output_val in puzzle[1]:
            if frozenset(output_val) in {segments[1], segments[4], segments[7], segments[8]}:
                num_times_1_4_7_8 += 1
    print(num_times_1_4_7_8)


def part_2():
    with open("input.txt") as indata:
        for line in indata:
            crabpos = [int(f) for f in line.split(",")]


if __name__ == "__main__":
    part_1()
