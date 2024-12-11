import argparse
import itertools
from collections import deque
from io import TextIOWrapper
from typing import NamedTuple

from rich import print
from tqdm.rich import tqdm

VERBOSE = False


def load_input(indata: TextIOWrapper):
    for row_idx, line in enumerate(indata):
        line = line.split("#")[0].strip()
        if not line:
            continue
        blocks = [int(i) for i in line]
        used_blocks = blocks[::2]
        free_blocks = blocks[1::2]
        return used_blocks, free_blocks


def part1(input_file: TextIOWrapper):
    used_blocks, free_blocks = load_input(input_file)
    defragmented_blocks = []
    used_blocks_queue = deque(used_blocks)
    file_id = 0
    last_file_id = len(used_blocks) - 1
    free_queue = deque(free_blocks)
    last_file_size = None
    while True:
        if VERBOSE:
            print(f"{defragmented_blocks=}")
        if len(used_blocks_queue) == 0:
            if last_file_size:
                defragmented_blocks.extend([last_file_id] * last_file_size)
            break
        used = used_blocks_queue.popleft()
        defragmented_blocks.extend([file_id] * used)

        file_id += 1
        free = free_queue.popleft()  # TODO: handle stopiteration
        if free is not None:
            while free > 0:
                # we have some free space where we can put the last file
                # 3 possible outcomes:
                # - last file is smaller than free space
                # - is the same as free space
                # - is larger than free space
                if last_file_size is None:
                    last_file_size = used_blocks_queue.pop()  # TODO: handle error when no more blocks

                if last_file_size <= free:
                    free -= last_file_size
                    defragmented_blocks.extend([last_file_id] * last_file_size)  # TODO: need id of the last file
                    last_file_id -= 1
                    last_file_size = None
                else:
                    defragmented_blocks.extend([last_file_id] * free)  # TODO: need id of the last file
                    last_file_size -= free
                    free = 0
    if VERBOSE:
        print(f"Final layout: {defragmented_blocks}")
    checksum = 0
    for idx, i in enumerate(defragmented_blocks):
        checksum += i * idx if i is not None else 0
    print(f"part 1: {checksum}")


class DiskEntry(NamedTuple):
    file_id: int | None  # None for free space
    size: int


def part2(input_file: TextIOWrapper):
    used_blocks, free_blocks = load_input(input_file)
    file_id = 0

    disk_layout = []
    for u, f in itertools.zip_longest(used_blocks, free_blocks):
        if f:
            disk_layout.extend((DiskEntry(file_id, u), DiskEntry(None, f)))
        else:
            disk_layout.append(DiskEntry(file_id, u))
        file_id += 1
    if VERBOSE:
        print(disk_layout)
    files_to_defrag = [dl for dl in disk_layout if dl.file_id is not None]
    with tqdm(total=len(files_to_defrag)) as pbar:
        while files_to_defrag:
            file_to_defrag = files_to_defrag.pop()
            for free_space_idx, layout_elem in enumerate(disk_layout):
                if layout_elem is file_to_defrag:
                    break  # don't move the file to the right
                if not (layout_elem.file_id is None and layout_elem.size >= file_to_defrag.size):
                    continue
                disk_layout[free_space_idx] = file_to_defrag
                if layout_elem.size > file_to_defrag.size:
                    disk_layout.insert(free_space_idx + 1, DiskEntry(None, layout_elem.size - file_to_defrag.size))
                # combine empty space
                old_idx = disk_layout.index(file_to_defrag, free_space_idx + 1)
                free_space_updated = False
                if old_idx + 1 < len(disk_layout) and (after := disk_layout[old_idx + 1]).file_id is None:
                    disk_layout[old_idx] = DiskEntry(None, after.size + file_to_defrag.size)
                    disk_layout.pop(old_idx + 1)
                    free_space_updated = True
                if old_idx - 1 > 0 and (before := disk_layout[old_idx - 1]).file_id is None:
                    # have to reference by disk_layout[old_idx] as it may have been changed above
                    disk_layout[old_idx - 1] = DiskEntry(None, before.size + disk_layout[old_idx].size)
                    disk_layout.pop(old_idx)
                    free_space_updated = True
                if not free_space_updated:
                    disk_layout[old_idx] = DiskEntry(None, file_to_defrag.size)
                if VERBOSE:
                    print(disk_layout)
                break
            # Increment the progress bar
            pbar.update(1)

    checksum = 0
    block_num = 0
    for i in disk_layout:
        if i.file_id is not None:
            for j in range(i.size):
                checksum += i.file_id * block_num
                block_num += 1
        else:
            block_num += i.size

    print(f"part 2: {checksum}  ({checksum:,})")
    # bad answers:
    # 6423236616653 (6,423,236,616,653) -- to low


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", type=int, choices=[1, 2])
    parser.add_argument("input", type=argparse.FileType("r"), default="test_input.txt")
    parser.add_argument("-v", "--verbose", action="store_true")
    arguments = parser.parse_args()
    global VERBOSE
    VERBOSE = arguments.verbose
    if arguments.part == 1:
        part1(arguments.input)
    elif arguments.part == 2:
        part2(arguments.input)


if __name__ == "__main__":
    main()
