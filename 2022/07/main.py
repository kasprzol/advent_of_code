from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from functools import cached_property


@dataclass
class File:
    name: str
    size: int = 0


@dataclass
class Dir:
    name: str
    parent: "Dir" | None = None
    dirs: list["Dir"] = field(default_factory=list)
    files: list[File] = field(default_factory=list)

    @cached_property
    def total_size(self) -> int:
        files_sum = sum(f.size for f in self.files)
        sub_dir_sum = sum(d.total_size for d in self.dirs)
        return files_sum + sub_dir_sum


def read_input() -> Dir:
    root = Dir("/", parent=None)
    curr_dir = root
    dir_stack = [root]
    cd_cmd = re.compile(r"\$ cd (.+)")
    file_entry = re.compile(r"(\d+) (.+)")
    dir_entry = re.compile(r"dir (.+)")
    ls_entry = re.compile(r"\$ ls")
    with open("input.txt") as indata:
        # input stacks
        for line in indata:
            line = line.strip()
            if match := cd_cmd.match(line):
                dir_name = match[1]
                if dir_name == "/":
                    curr_dir = root
                    dir_stack = [root]
                elif dir_name == "..":
                    assert len(dir_stack) > 1
                    dir_stack.pop()
                    curr_dir = dir_stack[-1]
                else:
                    new_dir = [d for d in curr_dir.dirs if d.name == dir_name]
                    assert len(new_dir) == 1, f"got more matching dirs: {new_dir}"
                    curr_dir = new_dir[0]
                    dir_stack.append(curr_dir)
            elif match := file_entry.match(line):
                f = File(name=match[2], size=int(match[1]))
                curr_dir.files.append(f)
            elif match := dir_entry.match(line):
                d = Dir(name=match[1], parent=curr_dir)
                curr_dir.dirs.append(d)
            elif ls_entry.match(line):
                continue
            else:
                assert False, f"Not matching line: {line}"
    return root


def part_1():
    max_dir_size = 100_000

    root = read_input()

    print(root)
    print(f"{root.total_size=}")
    total_size = 0
    dir_stack = [root]
    while dir_stack:
        d = dir_stack.pop(0)
        if (size := d.total_size) < max_dir_size:
            total_size += size
        [dir_stack.append(subdir) for subdir in d.dirs]
    print(total_size)


def part_2():
    total_fs_size = 70_000_000
    required_fs_size = 30_000_000
    root = read_input()
    used_size = root.total_size
    size_to_dir = defaultdict(list)
    dir_stack = [root]
    while dir_stack:
        d = dir_stack.pop(0)
        size_to_dir[d.total_size].append(d)
        [dir_stack.append(subdir) for subdir in d.dirs]

    for size in sorted(size_to_dir):
        if total_fs_size - (used_size - size) >= required_fs_size:
            for d in size_to_dir[size]:
                print(f"deleting directory {d.name} (of {size=}) would free required space.")
            return


if __name__ == '__main__':
    part_2()
