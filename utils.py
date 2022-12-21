from typing import NamedTuple

from dataclasses import dataclass


class Point(NamedTuple):
    x: int
    y: int


class Point3d(NamedTuple):
    x: int
    y: int
    z: int


@dataclass
class MutablePoint:
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))


@dataclass
class MutalbePoint3d:
    x: int
    y: int
    z: int

    def __hash__(self):
        return hash((self.x, self.y, self.z))


@dataclass
class Size:
    width: int
    height: int
