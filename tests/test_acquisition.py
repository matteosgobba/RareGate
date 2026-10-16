"""Exercise byte-level acquisition safety without network or real event data."""

import hashlib
import io
import json
from dataclasses import replace
from http.client import IncompleteRead
from pathlib import Path
from types import SimpleNamespace
from urllib.error import HTTPError, URLError
from urllib.request import Request

import pytest

from raregate.data import acquisition
from raregate.data.metadata import LHCO_RD, DatasetSource

PAYLOAD = b"verified LHCO fixture\n"


@pytest.fixture
def source() -> DatasetSource:
    """Keep the real source identity but replace integrity with tiny test bytes."""
    return replace(
        LHCO_RD,
        expected_size=len(PAYLOAD),
        expected_checksum=hashlib.md5(PAYLOAD, usedforsecurity=False).hexdigest(),
    )


def serve(
    monkeypatch: pytest.MonkeyPatch,
    payload: bytes = PAYLOAD,
    *,
    error: Exception | None = None,
    headers: dict[str, str] | None = None,
) -> list[int]:
    """Mock a streamed HTTPS response, recording bounded reads and request options."""
    reads: list[int] = []

    class Response(io.BytesIO):
        def read(self, size: int = -1) -> bytes:
            reads.append(size)
            if error is not None and len(reads) > 1:
                raise error
            return super().read(size)

    def open_response(request: Request, timeout: float) -> Response:
        assert request.full_url == LHCO_RD.url
        assert request.get_header("Accept-encoding") == "identity"
        assert timeout > 0
        response = Response(payload)
        response.headers = (
            {"Content-Length": str(len(payload))} if headers is None else headers
        )
        return response

    monkeypatch.setattr(acquisition, "urlopen", open_response)
    monkeypatch.setattr(acquisition, "CHUNK_SIZE", 4)
    return reads


def destination(data_dir: Path) -> Path:
    return acquisition.raw_directory(data_dir) / LHCO_RD.filename


def forbid_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected(*args: object, **kwargs: object) -> None:
        pytest.fail("Network must not be used in this path")

    monkeypatch.setattr(acquisition, "urlopen", unexpected)


def test_checksum_success(tmp_path: Path, source: DatasetSource) -> None:
    path = tmp_path / "fixture"
    path.write_bytes(PAYLOAD)
    integrity = acquisition.verify_file(path, source)
    assert integrity.verified_checksum == source.expected_checksum
    assert integrity.sha256 == hashlib.sha256(PAYLOAD).hexdigest()
    assert integrity.file_size == len(PAYLOAD)


def test_checksum_failure_same_size(tmp_path: Path, source: DatasetSource) -> None:
    path = tmp_path / "fixture"
    path.write_bytes(b"x" * len(PAYLOAD))
    with pytest.raises(acquisition.IntegrityError, match="MD5 mismatch"):
        acquisition.verify_file(path, source)


@pytest.mark.parametrize("payload", [b"short", PAYLOAD + b"long"])
def test_size_failure(tmp_path: Path, source: DatasetSource, payload: bytes) -> None:
    path = tmp_path / "fixture"
    path.write_bytes(payload)
    with pytest.raises(acquisition.IntegrityError, match="Size mismatch"):
        acquisition.verify_file(path, source)


def test_download_and_portable_manifest(
    tmp_path: Path, source: DatasetSource, monkeypatch: pytest.MonkeyPatch
) -> None:
    reads = serve(monkeypatch)
    result = acquisition.acquire(tmp_path, source=source)
    assert result.downloaded
    assert result.path == destination(tmp_path)
    assert result.path.read_bytes() == PAYLOAD
    assert reads and all(size == 4 for size in reads)
    assert not list(result.path.parent.glob("*.part"))
    manifest_path = result.path.with_name(f"{result.path.name}.manifest.json")
    manifest = json.loads(manifest_path.read_text())
    assert manifest["source"]["doi"] == LHCO_RD.doi
    assert manifest["source"]["expected_checksum"] == source.expected_checksum
    assert manifest["source"]["checksum_algorithm"] == "md5"
    assert manifest["verified_checksum"] == source.expected_checksum
    assert manifest["sha256"] == hashlib.sha256(PAYLOAD).hexdigest()
    assert manifest["file_size"] == len(PAYLOAD)
    assert manifest["acquisition_timestamp"] == manifest["verification_timestamp"]
    assert str(tmp_path) not in manifest_path.read_text()
    assert not list(result.path.parent.glob(".manifest-*.tmp"))


def test_reverification_skips_network_preserves_manifest(
    tmp_path: Path, source: DatasetSource, monkeypatch: pytest.MonkeyPatch
) -> None:
    serve(monkeypatch)
    first = acquisition.acquire(tmp_path, source=source)
    manifest_path = first.path.with_name(f"{first.path.name}.manifest.json")
    before = manifest_path.read_bytes(), manifest_path.stat().st_mtime_ns
    forbid_network(monkeypatch)
    second = acquisition.acquire(tmp_path, source=source)
    assert not second.downloaded
    assert second.integrity == first.integrity
    assert (manifest_path.read_bytes(), manifest_path.stat().st_mtime_ns) == before


def test_existing_valid_without_manifest_does_not_invent_acquisition_date(
    tmp_path: Path, source: DatasetSource, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = destination(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_bytes(PAYLOAD)
    forbid_network(monkeypatch)
    result = acquisition.acquire(tmp_path, source=source)
    manifest = json.loads(path.with_name(f"{path.name}.manifest.json").read_text())
    assert not result.downloaded
    assert manifest["acquisition_timestamp"] is None
    assert manifest["verification_timestamp"]


def test_invalid_existing_is_preserved(
    tmp_path: Path, source: DatasetSource, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = destination(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_bytes(b"x" * len(PAYLOAD))
    forbid_network(monkeypatch)
    with pytest.raises(acquisition.IntegrityError, match="--replace-invalid"):
        acquisition.acquire(tmp_path, source=source)
    assert path.read_bytes() == b"x" * len(PAYLOAD)
    assert list(path.parent.iterdir()) == [path]


def test_explicit_replacement_retains_invalid_bytes(
    tmp_path: Path, source: DatasetSource, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = destination(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_bytes(b"corrupted")
    serve(monkeypatch)
    result = acquisition.acquire(tmp_path, source=source, replace_invalid=True)
    assert result.downloaded and path.read_bytes() == PAYLOAD
    backups = list(path.parent.glob("*.invalid-*"))
    assert len(backups) == 1 and backups[0].read_bytes() == b"corrupted"


def test_download_checksum_failure_never_promotes(
    tmp_path: Path, source: DatasetSource, monkeypatch: pytest.MonkeyPatch
) -> None:
    serve(monkeypatch, b"x" * len(PAYLOAD))
    with pytest.raises(acquisition.IntegrityError, match="MD5 mismatch"):
        acquisition.acquire(tmp_path, source=source)
    assert list(destination(tmp_path).parent.iterdir()) == []


def test_failed_replacement_keeps_original(
    tmp_path: Path, source: DatasetSource, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = destination(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_bytes(b"corrupted")
    serve(monkeypatch, b"x" * len(PAYLOAD))
    with pytest.raises(acquisition.IntegrityError):
        acquisition.acquire(tmp_path, source=source, replace_invalid=True)
    assert path.read_bytes() == b"corrupted"
    assert list(path.parent.iterdir()) == [path]


@pytest.mark.parametrize(
    "error",
    [
        URLError("connection reset"),
        TimeoutError("socket timeout"),
        IncompleteRead(b"x"),
    ],
)
def test_interrupted_stream_cleanup(
    tmp_path: Path,
    source: DatasetSource,
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
) -> None:
    serve(monkeypatch, error=error)
    with pytest.raises(type(error)):
        acquisition.acquire(tmp_path, source=source)
    assert list(destination(tmp_path).parent.iterdir()) == []


def test_http_error_cleanup(
    tmp_path: Path, source: DatasetSource, monkeypatch: pytest.MonkeyPatch
) -> None:
    def failure(*args: object, **kwargs: object) -> None:
        raise HTTPError(LHCO_RD.url, 503, "unavailable", {}, None)

    monkeypatch.setattr(acquisition, "urlopen", failure)
    with pytest.raises(HTTPError):
        acquisition.acquire(tmp_path, source=source)
    assert list(destination(tmp_path).parent.iterdir()) == []


@pytest.mark.parametrize("length", ["bad", "1"])
def test_unexpected_content_length_cleanup(
    tmp_path: Path, source: DatasetSource, monkeypatch: pytest.MonkeyPatch, length: str
) -> None:
    serve(monkeypatch, headers={"Content-Length": length})
    with pytest.raises(acquisition.IntegrityError, match="HTTP Content-Length"):
        acquisition.acquire(tmp_path, source=source)
    assert list(destination(tmp_path).parent.iterdir()) == []


@pytest.mark.parametrize("payload", [b"short", PAYLOAD + b"long"])
def test_lengthless_response_still_requires_exact_bytes(
    tmp_path: Path,
    source: DatasetSource,
    monkeypatch: pytest.MonkeyPatch,
    payload: bytes,
) -> None:
    serve(monkeypatch, payload, headers={})
    with pytest.raises(acquisition.IntegrityError):
        acquisition.acquire(tmp_path, source=source)
    assert list(destination(tmp_path).parent.iterdir()) == []


def test_stale_partial_is_not_overwritten(
    tmp_path: Path, source: DatasetSource, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = destination(tmp_path)
    path.parent.mkdir(parents=True)
    partial = path.with_name(f"{path.name}.part")
    partial.write_bytes(b"previous partial")
    forbid_network(monkeypatch)
    with pytest.raises(
        acquisition.AcquisitionError, match="Another download may be active"
    ):
        acquisition.acquire(tmp_path, source=source)
    assert partial.read_bytes() == b"previous partial"
    assert not path.exists()


def test_verify_only_missing_never_downloads(
    tmp_path: Path, source: DatasetSource, monkeypatch: pytest.MonkeyPatch
) -> None:
    forbid_network(monkeypatch)
    with pytest.raises(acquisition.AcquisitionError, match="Missing artifact"):
        acquisition.acquire(tmp_path, source=source, verify_only=True)
    assert not destination(tmp_path).parent.exists()


def test_insufficient_disk_space(
    tmp_path: Path, source: DatasetSource, monkeypatch: pytest.MonkeyPatch
) -> None:
    forbid_network(monkeypatch)
    monkeypatch.setattr(
        acquisition.shutil, "disk_usage", lambda path: SimpleNamespace(free=1)
    )
    with pytest.raises(acquisition.AcquisitionError, match="Insufficient free space"):
        acquisition.acquire(tmp_path, source=source)
    assert list(destination(tmp_path).parent.iterdir()) == []


def test_destination_from_nested_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "raregate"\n')
    nested = tmp_path / "notebooks" / "exploration"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)
    assert acquisition.raw_directory() == tmp_path / "data/raw/lhco/6466204"


def test_outside_checkout_requires_explicit_data_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        acquisition, "__file__", str(tmp_path / "installed/acquisition.py")
    )
    with pytest.raises(acquisition.AcquisitionError, match="--data-dir"):
        acquisition.raw_directory()
    assert acquisition.raw_directory(tmp_path) == tmp_path / "raw/lhco/6466204"


def test_cli_reports_failure_without_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    forbid_network(monkeypatch)
    monkeypatch.setattr(
        acquisition.sys,
        "argv",
        ["acquisition", "--data-dir", str(tmp_path), "--verify-only"],
    )
    assert acquisition.main() == 1
    assert "Acquisition failed: Missing artifact" in capsys.readouterr().err


@pytest.mark.parametrize("kind", ["directory", "symlink"])
def test_unsafe_destination_is_refused(
    tmp_path: Path, source: DatasetSource, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    path = destination(tmp_path)
    path.parent.mkdir(parents=True)
    if kind == "directory":
        path.mkdir()
    else:
        target = tmp_path / "actual-file"
        target.write_bytes(PAYLOAD)
        path.symlink_to(target)
    forbid_network(monkeypatch)
    with pytest.raises(acquisition.AcquisitionError, match="regular file|symlink"):
        acquisition.acquire(tmp_path, source=source, replace_invalid=True)
    assert path.exists()


def test_unreadable_manifest_is_rebuilt_from_verified_bytes(
    tmp_path: Path, source: DatasetSource, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = destination(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_bytes(PAYLOAD)
    manifest_path = path.with_name(f"{path.name}.manifest.json")
    manifest_path.write_text("not JSON")
    forbid_network(monkeypatch)
    acquisition.acquire(tmp_path, source=source)
    manifest = json.loads(manifest_path.read_text())
    assert manifest["verified_checksum"] == source.expected_checksum
    assert manifest["sha256"] == hashlib.sha256(PAYLOAD).hexdigest()
    assert manifest["acquisition_timestamp"] is None
