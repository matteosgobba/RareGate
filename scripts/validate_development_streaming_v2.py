"""Task0053 explicit generated v2 qualification; no operational backend or grant."""

import sys

sys.dont_write_bytecode = True


def main():
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-generated-v2", action="store_true")
    parser.add_argument("--subject", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--root", required=False)
    parser.add_argument("--suite", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    if not args.root or args.run_generated_v2 == args.subject:
        parser.error(
            "Explicit generated activation, root, and exclusive observer/subject mode required"
        )
    from raregate.streaming.validation_v2 import observe, subject

    if args.subject:
        return subject(Path(args.root), args.suite)
    result = observe(Path(args.root), args.suite)
    print(
        {
            k: result[k]
            for k in ("qualified", "subject_lifetime_ns", "problem", "bundle_sha256")
        }
    )
    return int(not result["qualified"])


if __name__ == "__main__":
    raise SystemExit(main())
