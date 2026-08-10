"""stats-cli entry point: print count, mean, and median for CLI number args."""

import sys

from statslib import mean, median, parse_numbers


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python stats.py <number> [<number> ...]")
        return 1

    values = parse_numbers(argv)
    print(f"count: {len(values)}")
    print(f"mean:  {mean(values)}")
    print(f"median: {median(values)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
