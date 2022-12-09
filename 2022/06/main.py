from  pathlib import Path


def part_1():
    text = Path("input.txt").read_text()

    for i in range(len(text)-3):
        marker = text[i:i+4]
        is_marker = len(set(marker)) == 4
        if is_marker:
            print(i+4)
            break


def part_2():
    text = Path("input.txt").read_text()
    header_len = 14

    for i in range(len(text)-header_len):
        marker = text[i:i+header_len]
        is_marker = len(set(marker)) == header_len
        if is_marker:
            print(i+header_len)
            break


if __name__ == '__main__':
    part_2()
