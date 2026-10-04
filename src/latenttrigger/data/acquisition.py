"""Acquire the pinned LHCO artifact; never accept existence as verification."""

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import tomllib
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from http.client import HTTPException
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from latenttrigger.data.metadata import LHCO_RD, DatasetSource

CHUNK_SIZE = 1024 * 1024


class AcquisitionError(RuntimeError):
    """An artifact could not be safely acquired or verified."""


class IntegrityError(AcquisitionError):
    """A local file differs from the pinned source."""


@dataclass(frozen=True)
class Integrity:
    """Actual byte count, publisher checksum, and independent SHA-256."""

    file_size: int
    verified_checksum: str
    sha256: str


@dataclass(frozen=True)
class AcquisitionResult:
    """Verified destination and whether this invocation downloaded it."""

    path: Path
    integrity: Integrity
    downloaded: bool


def raw_directory(data_dir: Path | None = None) -> Path:
    """Resolve an explicit data root, or find this checkout from cwd/package."""
    if data_dir is None:
        for anchor in (Path.cwd(), Path(__file__).resolve().parent):
            for candidate in (anchor, *anchor.parents):
                config = candidate / "pyproject.toml"
                if config.is_file():
                    project = tomllib.loads(config.read_text()).get("project", {})
                    if project.get("name") == "latent-trigger":
                        data_dir = candidate / "data"
                        break
            if data_dir is not None:
                break
    if data_dir is None:
        raise AcquisitionError("Checkout not found; specify --data-dir <data-root>.")
    return data_dir.expanduser().resolve() / "raw" / "lhco" / str(LHCO_RD.record_id)


def verify_file(path: Path, source: DatasetSource = LHCO_RD) -> Integrity:
    """Stream-check size and publisher MD5; also compute SHA-256 for provenance."""
    if path.is_symlink():
        raise AcquisitionError(f"Refusing a symlink artifact: {path}")
    size = path.stat().st_size
    if size != source.expected_size:
        raise IntegrityError(
            f"Size mismatch for {path.name}: expected {source.expected_size}, got {size}"
        )
    checksum = hashlib.md5(usedforsecurity=False)
    sha256 = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_SIZE):
            checksum.update(chunk)
            sha256.update(chunk)
    actual = checksum.hexdigest()
    if actual != source.expected_checksum:
        raise IntegrityError(
            f"MD5 mismatch for {path.name}: expected {source.expected_checksum}, got {actual}"
        )
    return Integrity(size, actual, sha256.hexdigest())


def _download(
    partial: Path,
    source: DatasetSource,
    timeout: float,
    report: Callable[[str], None],
) -> None:
    """Use an exclusive partial file; remove only this invocation's failed bytes."""
    try:
        output = partial.open("xb")
    except FileExistsError as error:
        raise AcquisitionError(
            f"Partial file already exists: {partial}. Another download may be active. "
            "After confirming no download is running, remove the stale .part and retry."
        ) from error
    succeeded = False
    try:
        request = Request(
            source.url,
            headers={
                "User-Agent": "LatentTrigger/0.1.0",
                "Accept-Encoding": "identity",
            },
        )
        with output, urlopen(request, timeout=timeout) as response:
            encoding = response.headers.get("Content-Encoding", "identity")
            if encoding != "identity":
                raise AcquisitionError(f"Unexpected HTTP content encoding: {encoding}")
            length = response.headers.get("Content-Length")
            if length is not None:
                try:
                    length_matches = int(length) == source.expected_size
                except ValueError:
                    length_matches = False
                if not length_matches:
                    raise IntegrityError(f"Unexpected HTTP Content-Length: {length}")
            total = 0
            next_progress = 10
            while chunk := response.read(CHUNK_SIZE):
                total += len(chunk)
                if total > source.expected_size:
                    raise IntegrityError("Response exceeds the pinned byte count.")
                output.write(chunk)
                percent = total * 100 // source.expected_size
                if percent >= next_progress:
                    report(f"Downloaded {total:,} / {source.expected_size:,} bytes")
                    next_progress = (percent // 10 + 1) * 10
            output.flush()
            os.fsync(output.fileno())
        succeeded = True
    finally:
        output.close()
        if not succeeded:
            partial.unlink(missing_ok=True)


def _write_manifest(
    path: Path,
    source: DatasetSource,
    integrity: Integrity,
    downloaded: bool,
    report: Callable[[str], None],
) -> None:
    """Write portable local state atomically; preserve unchanged verified state."""
    manifest_path = path.with_name(f"{path.name}.manifest.json")
    facts = {
        "manifest_version": 1,
        "source": asdict(source),
        "local_file": path.name,
        **asdict(integrity),
    }
    if not downloaded and manifest_path.exists():
        try:
            previous = json.loads(manifest_path.read_text())
            if isinstance(previous, dict) and all(
                previous.get(key) == value for key, value in facts.items()
            ):
                return
        except (ValueError, OSError):
            pass
        report("Local manifest is stale or unreadable; rebuilding verified state.")
    timestamp = datetime.now(UTC).isoformat()
    payload = {
        **facts,
        "acquisition_timestamp": timestamp if downloaded else None,
        "verification_timestamp": timestamp,
    }
    # An externally supplied valid file has an unknown acquisition date.
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", dir=path.parent, prefix=".manifest-", suffix=".tmp", delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(manifest_path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def acquire(
    data_dir: Path | None = None,
    *,
    replace_invalid: bool = False,
    verify_only: bool = False,
    timeout: float = 60,
    source: DatasetSource = LHCO_RD,
    report: Callable[[str], None] = print,
) -> AcquisitionResult:
    """Verify/reuse, or stream/download/verify/promote the pinned raw artifact.

    Replacement requires explicit permission and retains invalid bytes in a
    sibling .invalid-* file. Failed transfers are cleaned; abrupt termination
    leaves an exclusive .part requiring deliberate removal. There is no resume.
    """
    if timeout <= 0:
        raise AcquisitionError("Timeout must be positive.")
    directory = raw_directory(data_dir)
    destination = directory / source.filename
    report(f"Dataset: {source.dataset} {source.version} ({source.doi})")
    report(f"Destination: {destination}")
    if destination.is_symlink():
        raise AcquisitionError(f"Refusing a symlink artifact: {destination}")
    invalid = False
    if destination.exists():
        if not destination.is_file():
            raise AcquisitionError(f"Destination is not a regular file: {destination}")
        report("Existing file: verifying size, MD5, and SHA-256.")
        try:
            integrity = verify_file(destination, source)
        except IntegrityError as error:
            if verify_only or not replace_invalid:
                raise IntegrityError(
                    f"{error}. File preserved; use --replace-invalid to replace safely."
                ) from error
            invalid = True
            report(f"{error}. Explicit replacement requested; preserving old bytes.")
        else:
            _write_manifest(destination, source, integrity, False, report)
            report("Verified existing file; download not required.")
            return AcquisitionResult(destination, integrity, False)
    if verify_only:
        raise AcquisitionError(f"Missing artifact: {destination}; verification only.")
    directory.mkdir(parents=True, exist_ok=True)
    required = source.expected_size + 64 * 1024 * 1024
    free = shutil.disk_usage(directory).free
    if free < required:
        raise AcquisitionError(
            f"Insufficient free space: need {required:,}, have {free:,}"
        )
    partial = destination.with_name(f"{destination.name}.part")
    report(
        f"Download required: {source.expected_size:,} bytes; free space {free:,} bytes."
    )
    _download(partial, source, timeout, report)
    try:
        report("Download complete: verifying before promotion.")
        integrity = verify_file(partial, source)
        if invalid:
            backup = destination.with_name(f"{destination.name}.invalid-{uuid4().hex}")
            destination.replace(backup)
            report(f"Previous invalid file retained at: {backup}")
        partial.replace(destination)
    finally:
        partial.unlink(missing_ok=True)
    _write_manifest(destination, source, integrity, True, report)
    report(f"Verified and accepted: MD5 {integrity.verified_checksum}")
    return AcquisitionResult(destination, integrity, True)


def main() -> int:
    """Run acquisition without requiring notebook execution or audit dependencies."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-dir", type=Path, help="Data root containing raw/ (portable)"
    )
    parser.add_argument("--replace-invalid", action="store_true")
    parser.add_argument("--verify-only", action="store_true", help="Never download")
    parser.add_argument(
        "--timeout", type=float, default=60, help="Socket timeout, seconds"
    )
    args = parser.parse_args()
    try:
        acquire(
            args.data_dir,
            replace_invalid=args.replace_invalid,
            verify_only=args.verify_only,
            timeout=args.timeout,
        )
    except (AcquisitionError, OSError, URLError, HTTPException) as error:
        print(f"Acquisition failed: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Acquisition interrupted; owned partial bytes cleaned.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
