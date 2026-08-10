"""Core statistics helpers for the stats-cli sample.

Kept intentionally simple. Contains one seeded bug (see median) used for the
course live demo, and a function the hands-on exercise will harden.
"""

from typing import List


def parse_numbers(tokens: List[str]) -> List[float]:
    """Turn a list of string tokens into floats.

    NOTE (hands-on): this currently trusts its input. The exercise is to add
    validation that rejects non-numeric tokens with a clear error, plus a test.
    """
    return [float(t) for t in tokens]


def mean(values: List[float]) -> float:
    """Arithmetic mean of the values."""
    return sum(values) / len(values)


def median(values: List[float]) -> float:
    """Median of the values.

    SEEDED BUG (demo): for an even-length list this returns the higher of the
    two middle elements instead of their average. `test_median_even` fails.
    """
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid]
