"""Task0058 explicit generated qualification or one conditionally authorized AE pilot."""

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
    parser.add_argument("--group", type=int, choices=(1,), default=1)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    if Path(args.root) != repo / "data/task0058-validation/ae-pilot-v1":
        parser.error("Only the new Task0058 AE-only root")
    from latenttrigger.streaming import pilot54, pilot58, startup55

    root = Path(args.root)
    if args.subject or args.qualify_generated:
        startup55.install_payload_denial(repo, root)
    if args.subject:
        return startup55.subject(root, args.group, context=pilot58)
    if args.pilot_subject:
        return pilot54.pilot_subject(root, context=pilot58.context(root, repo))
    if args.qualify_generated:
        result = startup55.observe(root, args.group, context=pilot58)
    else:
        result = pilot54.observe_pilot(root, context=pilot58.context(root, repo))
    print(
        {
            k: result.get(k)
            for k in ("qualified", "problem", "subject_lifetime_ns", "bundle_sha256")
        }
    )
    return int(not result["qualified"])


if __name__ == "__main__":
    raise SystemExit(main())
