def read_boards(indata) -> list[list[list[int]]]:
    boards = []
    board = []
    for line in indata:
        line = line.strip()
        if not line:
            boards.append(board)
            board = []
            continue
        board.append([int(num) for num in line.split(" ") if num.strip()])
    if board:
        boards.append(board)
    print(boards)
    return boards


class Marker():
    def __repr__(self):
        return "*"


def part_1():
    marker = Marker()
    numbers: list[int] = None
    boards: list[list[list[int | object]]] = []
    with open("input.txt") as indata:
        numbers = [int(num) for num in indata.readline().strip().split(",")]
        indata.readline()  # blank line

        boards = read_boards(indata)

    for num in numbers:
        for board in boards:
            for row in board:
                for idx, cell in enumerate(row):
                    if num == cell:
                        row[idx] = marker
                        break
            if any(
                    (all(row_num == marker for row_num in row) for row in board)
            ) or any(
                all(board[row_num][col] == marker for row_num in range(5)) for col in range(5)
            ):
                board_sum = sum(sum([cell for cell in row if cell != marker], 0) for row in board)
                score = board_sum * num
                print(f"wining board after number {num} * {board_sum=} = {score}:\n{board}")
                return


def part_2():
    marker = Marker()
    numbers: list[int] = None
    boards: list[list[list[int | object]]] = []
    with open("input.txt") as indata:
        numbers = [int(num) for num in indata.readline().strip().split(",")]
        indata.readline()  # blank line

        boards = read_boards(indata)

    for num in numbers:
        board_pop = None
        while True:
            for board_idx, board in enumerate(boards):
                for row in board:
                    for idx, cell in enumerate(row):
                        if num == cell:
                            row[idx] = marker
                            break
                if board and (any(
                        (all(row_num == marker for row_num in row) for row in board)
                ) or any(
                    all(board[row_num][col] == marker for row_num in range(5)) for col in range(5)
                )):
                    board_sum = sum(sum([cell for cell in row if cell != marker], 0) for row in board)
                    score = board_sum * num
                    print(f"wining board {board_idx+1} after number {num} * {board_sum=} = {score}. "
                            f"{len(boards) - 1} boards left:\n{board}")
                    if len(boards) == 1:  # the last board
                        print(f"Final board {board_idx + 1} after number {num} * {board_sum=} = {score}.")
                        return
                    else:
                        board_pop = board_idx
                        break
            if board_pop is not None:
                boards.pop(board_pop)
                board_pop = None
            else:
                break


if __name__ == '__main__':
    part_2()
