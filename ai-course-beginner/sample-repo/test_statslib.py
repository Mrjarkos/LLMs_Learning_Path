"""Tests for statslib.

`test_median_even` is RED on purpose — it's the demo bug. Everything else is
green so attendees can see a clean run once the agent fixes the median.
"""

import pytest

from statslib import mean, median, parse_numbers


def test_parse_numbers_basic():
    assert parse_numbers(["1", "2.5", "3"]) == [1.0, 2.5, 3.0]


def test_mean_basic():
    assert mean([2, 4, 6]) == 4.0


def test_median_odd():
    assert median([3, 1, 2]) == 2.0


def test_median_even():
    # SEEDED BUG: median of an even list should be the average of the two
    # middle values -> (2 + 3) / 2 == 2.5. Current code returns 3.
    assert median([1, 2, 3, 4]) == 2.5
