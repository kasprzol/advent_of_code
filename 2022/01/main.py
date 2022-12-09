from pathlib import Path
from typing import Sequence, Iterable


def yield_elves() -> Iterable[int]:
    elf_sum = 0
    with Path("input.txt").open() as data:
        for line in data.readlines():
            if line in ( "", "\n"):
                yield elf_sum
                elf_sum = 0
                continue
            elf_sum += int(line)
    yield elf_sum

def main():
    elves = list(yield_elves())
    most_calories = sum(sorted(elves, reverse=True)[:3])

    print(elves)
    print(most_calories)

    return 0

if __name__ == '__main__':
    main()