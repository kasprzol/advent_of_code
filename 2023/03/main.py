import re
from collections.abc import Iterable




def part1():
    value = 0
    r_num = re.compile("\\d+")
    r_symbol = re.compile("[^0-9.]")
    lines = list(map(str.strip, open("input.txt").readlines()))
    found_symbols = set()
    for line_no, line in enumerate(lines):
        for match in r_num.finditer(line):
            is_part_num = False
            start_line = line_no - (1 if line_no > 0 else 0)
            end_line = line_no + (1 if line_no < len(lines) - 1 else 0)
            match_idx = match.span()
            if match_idx[0] > 0:
                match_idx = match_idx[0] - 1, match_idx[1]
            if match_idx[1] < len(line):
                match_idx = match_idx[0], match_idx[1] + 1
            for line_to_check in lines[start_line:end_line+1]:
                if r_symbol.search(line_to_check[match_idx[0]:match_idx[1]]):
                #for candidate in line_to_check[match_idx[0]:match_idx[1]+1]:
                #    if not candidate.isnumeric() and candidate != ".":
                        is_part_num = True
                        #found_symbols.add(candidate)
                        break
                if is_part_num:
                    break

            if is_part_num:
                value += int(match[0])

    print(f"The value is {value}")
    # print(f"{found_symbols=}")



def part2():
    ...



if __name__ == '__main__':
    part1()
