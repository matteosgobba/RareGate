"""Task0057 generated-only core and shared sequential session qualification."""

import sys

sys.dont_write_bytecode = True


def main():
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--qualify-generated", action="store_true")
    modes.add_argument("--subject", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--root", required=True)
    parser.add_argument("--group", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    if Path(args.root) != repo / "data/task0057-validation/session-lifecycle":
        parser.error("Only the owned Task0057 generated root; no operational mode")
    from latenttrigger.streaming import session57, startup55

    root = Path(args.root)
    startup55.install_payload_denial(repo, root)
    if args.subject:
        return startup55.subject(root, args.group, context=session57)
    result = startup55.observe(root, args.group, context=session57)
    print(
        {
            k: result.get(k)
            for k in ("qualified", "problem", "subject_lifetime_ns", "bundle_sha256")
        }
    )
    return int(not result["qualified"])


if __name__ == "__main__":
    raise SystemExit(main())
