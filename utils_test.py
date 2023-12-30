import pytest

from utils import range_intersection


@pytest.mark.parametrize(
    ("range_a", "range_b", "expected"),
    (
        ((1, 10), (1, 5), (None, (1, 5), (6, 5))),
        ((1, 10), (1, 10), (None, (1, 10), None)),
        ((1, 10), (5, 10), ((1, 4), (5, 6), (11, 4))),
        ((5, 10), (10, 5), ((5, 5), (10, 5), None)),
        ((1, 1), (1, 1), (None, (1, 1), None)),
        # disjoined
        ((1, 10), (20, 10), ((1, 10), None, (20, 10))),
        ((100, 10), (1, 10), ((1, 10), None, (100, 10))),
        # wrong order
        ((10, 10), (5, 10), ((5, 5), (10, 5), (15, 5))),
        # 1 element
        ((10, 10), (1, 10), ((1, 9), (10, 1), (11, 9))),
        ((0, 1), (0, 1), (None, (0, 1), None)),
    ),
)
def test_range_intersection(range_a, range_b, expected):
    assert expected == range_intersection(range_a, range_b)
