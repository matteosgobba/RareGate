"""Reproduce Task 0004 integrity, split assignment and training-only EDA."""

import argparse
import json
from pathlib import Path

from latenttrigger.data.acquisition import acquire
from latenttrigger.data.analysis import CHUNK_ROWS, scan_and_split
from latenttrigger.data.eda import plot_eda, training_eda
from latenttrigger.data.splitting import PROTOCOL


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chunk-rows", type=int, default=CHUNK_ROWS)
    parser.add_argument("--scan-only", action="store_true")
    parser.add_argument(
        "--reuse-scan",
        action="store_true",
        help="Verify and reuse saved membership instead of rehashing events",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.reuse_scan:
        verified = acquire(data_dir=root / "data", verify_only=True)
        report = json.loads(
            (root / "data/analysis" / PROTOCOL / "split-manifest.json").read_text()
        )
        if verified.integrity.sha256 != report["source_integrity"]["sha256"]:
            raise ValueError("Raw source differs from the split manifest.")
    else:
        report = scan_and_split(root, chunk_rows=args.chunk_rows)
    if not args.scan_only:
        config = training_eda(root, report, chunk_rows=args.chunk_rows)
        plot_eda(root, config)


if __name__ == "__main__":
    main()
