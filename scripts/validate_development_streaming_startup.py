"""Task0055 source-free streaming/runtime qualification. No operational mode."""

import sys

sys.dont_write_bytecode = True


def main():
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--qualify-source-free", action="store_true")
    modes.add_argument("--subject", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--root", required=True)
    parser.add_argument("--group", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    if Path(args.root) != repo / "data/task0055-validation/task0055":
        parser.error("Only the new fixed Task0055 source-free root")
    from raregate.streaming.startup55 import observe, subject

    if args.subject:
        return subject(Path(args.root), args.group)
    result = observe(Path(args.root), args.group)
    print(
        {
            k: result[k]
            for k in ("qualified", "subject_lifetime_ns", "problem", "bundle_sha256")
        }
    )
    return int(not result["qualified"])


if __name__ == "__main__":
    raise SystemExit(main())
