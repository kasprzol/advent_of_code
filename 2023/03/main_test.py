import pytest
from main import find_gear_ratio

@pytest.mark.parametrize(
        ("lines", "expected_ratio"),
        # fmt: off
        (
            (("467...",
              "...*..",
              "..35..",), 467 * 35),
             (("....755.",
               "...*....",
               "...598..",), 755 * 598),
            (("617*....",), 0),
            (("12*34",), 12*34),
        )
        # fmt: on
)
def test_find_gear_ratio(lines, expected_ratio):
    actual_ratio = find_gear_ratio(lines)

    assert actual_ratio == expected_ratio