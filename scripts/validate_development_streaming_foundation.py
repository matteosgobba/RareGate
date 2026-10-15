"""Explicit generated fixture validation only; import/help have no run side effects."""

import argparse
import json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-generated-fixtures",
        action="store_true",
        help="explicitly activate bounded in-memory fixtures",
    )
    parser.add_argument(
        "--output", help="new absolute directory under data/task0051-validation or /tmp"
    )
    parser.add_argument(
        "--scenario",
        action="append",
        choices=(
            "normal_wrap",
            "capacity",
            "contention",
            "die_before_return",
            "die_after_return",
            "die_after_output",
            "die_with_mutex",
            "failed_start",
        ),
    )
    args = parser.parse_args(argv)
    if not args.run_generated_fixtures or not args.output:
        parser.error(
            "Explicit --run-generated-fixtures and --output required; no operational mode"
        )
    from latenttrigger.streaming.fixture import SCENARIOS, validate_generated

    result = validate_generated(
        args.output, tuple(args.scenario) if args.scenario else tuple(SCENARIOS)
    )
    print(
        json.dumps(
            {
                "fixture_only": True,
                "attempts": len(result["attempts"]),
                "configured_offers": result["configured_offers"],
                "elapsed_ns": result["elapsed_ns"],
                "diagnostic_bytes": result["diagnostic_bytes"],
            }
        )
    )
    return 0 if result["software_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
