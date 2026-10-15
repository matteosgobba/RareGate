"""Explicit Task0054 generated qualification or single conditional development pilot."""

import sys

sys.dont_write_bytecode = True


def main():
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--qualify-generated", action="store_true")
    group.add_argument("--run-pilot", action="store_true")
    group.add_argument(
        "--generated-subject", action="store_true", help=argparse.SUPPRESS
    )
    group.add_argument("--pilot-subject", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--root", required=True)
    parser.add_argument("--suite", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()
    from latenttrigger.streaming.pilot54 import ROOT_NAME

    root = Path(args.root)
    repo = Path(__file__).resolve().parents[1]
    if root != repo / "data/task0054-validation" / ROOT_NAME:
        parser.error("Only the fixed new Task0054 owned root")
    if args.qualify_generated:
        from latenttrigger.streaming.validation_v2 import observe

        result = observe(root, args.suite, task="0054")
    elif args.generated_subject:
        from latenttrigger.streaming.validation_v2 import subject

        return subject(root, args.suite)
    elif args.pilot_subject:
        from latenttrigger.streaming.pilot54 import pilot_subject

        return pilot_subject(root)
    else:
        from latenttrigger.streaming.pilot54 import observe_pilot

        result = observe_pilot(root)
    print(
        {
            k: result[k]
            for k in ("qualified", "subject_lifetime_ns", "problem", "bundle_sha256")
        }
    )
    return int(not result["qualified"])


if __name__ == "__main__":
    raise SystemExit(main())
