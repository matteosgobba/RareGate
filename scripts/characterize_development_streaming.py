"""Explicit Task0052 generated-only characterization. Help/import do no work."""

import argparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-generated-characterization", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    if not args.run_generated_characterization or not args.output:
        parser.error("Explicit generated activation and fresh absolute output required")
    from raregate.streaming.characterization import characterize

    result = characterize(args.output)
    print(
        {
            k: result[k]
            for k in (
                "invocation_count",
                "configured_offers",
                "elapsed_ns",
                "unattempted",
            )
        }
    )
    return int(
        bool(result["unattempted"])
        or any(not r["software_checks_passed"] for r in result["attempts"])
    )


if __name__ == "__main__":
    raise SystemExit(main())
