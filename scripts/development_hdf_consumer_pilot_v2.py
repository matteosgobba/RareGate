"""Task0056 explicit generated qualification or newly authorized narrow real pilot."""

import sys

sys.dont_write_bytecode = True


def main():
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--qualify-generated", action="store_true")
    modes.add_argument("--subject", action="store_true", help=argparse.SUPPRESS)
    modes.add_argument("--run-pilot", action="store_true")
    modes.add_argument("--pilot-subject", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--root", required=True)
    parser.add_argument("--group", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    if Path(args.root) != repo / "data/task0056-validation/session-v2":
        parser.error("Only the new Task0056 canonical root")
    from latenttrigger.streaming import pilot54, pilot56, startup55

    root = Path(args.root)
    if args.subject:
        return startup55.subject(root, args.group, context=pilot56)
    if args.pilot_subject:
        return pilot54.pilot_subject(root, context=pilot56.context(root, repo))
    if args.qualify_generated:
        result = startup55.observe(root, args.group, context=pilot56)
    else:
        result = pilot54.observe_pilot(root, context=pilot56.context(root, repo))
    print(
        {
            k: result.get(k)
            for k in ("qualified", "problem", "subject_lifetime_ns", "bundle_sha256")
        }
    )
    return int(not result["qualified"])


if __name__ == "__main__":
    raise SystemExit(main())
