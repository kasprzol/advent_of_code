

def part_1():
    SCORES = {
        "A": {  # rock
            "X": 1 + 3,  # rock
            "Y": 2 + 6,  # paper
            "Z": 3 + 0,  # scissors
        },
        "B": {  # paper
            "X": 1 + 0,  # rock
            "Y": 2 + 3,  # paper
            "Z": 3 + 6,  # scissors
        },
        "C": {  # scissors
            "X": 1 + 6,  # rock
            "Y": 2 + 0,  # paper
            "Z": 3 + 3,  # scissors
        },
    }

    total_score = 0
    with open("input.txt", "r") as indata:
        for line in indata:
            opponent_hand, my_hand = line.split()
            total_score += SCORES[opponent_hand][my_hand]

    print(total_score)
    return 0

def part_2():
    SCORES = {
        # X - lose, Y - draw, Z - win
        "A": {  # rock
            "X": 3 + 0,
            "Y": 1 + 3,
            "Z": 2 + 6,
        },
        "B": {  # paper
            "X": 1 + 0,
            "Y": 2 + 3,
            "Z": 3 + 6,
        },
        "C": {  # scissors
            "X": 2 + 0,
            "Y": 3 + 3,
            "Z": 1 + 6,
        },
    }

    total_score = 0
    with open("input.txt", "r") as indata:
        for line in indata:
            opponent_hand, my_hand = line.split()
            total_score += SCORES[opponent_hand][my_hand]

    print(total_score)
    return 0

if __name__ == '__main__':
    part_2()

