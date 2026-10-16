"""Bounded transport, runtime receipts and exclusive source-bound stage ledger."""

import hashlib
import importlib.metadata
import io
import json
import os
import platform
import resource
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from contextlib import redirect_stdout
from datetime import UTC, datetime
from pathlib import Path

from .data import digest, write_json

ROOT = Path(__file__).resolve().parents[4]
CONFIG = ROOT / "configs/research/decisive_adc_preparation_v2.json"


def utc():
    return datetime.now(UTC).isoformat()


def read_config():
    config = json.loads(CONFIG.read_text())
    protocol_path = ROOT / config["protocol_path"]
    if digest(protocol_path) != config["protocol_sha256"]:
        raise ValueError("immutable protocol changed")
    if (
        config["scope"] != "Task0061-real-ADC-preparation-only"
        or config["Task0062_authorized"]
    ):
        raise PermissionError("Task0061 scope only")
    return config, json.loads(protocol_path.read_text())


def behavioral_bundle():
    paths = [
        CONFIG,
        ROOT / "docs/prompts/0061-adc-preparation-training-freeze.md",
        ROOT / "configs/research/decisive_scientific_experiment_v2.json",
        ROOT / "scripts/prepare_decisive_adc_experiment.py",
        ROOT / "scripts/validate_decisive_adc.py",
        ROOT / "tests/test_decisive_adc.py",
        ROOT / "tests/decisive_adc_plugin.py",
        ROOT / "docs/project-scientific-audit.md",
        ROOT / "docs/decisive-scientific-experiment.md",
        ROOT / "results/tables/final/task0060-scientific-audit-summary.json",
        ROOT / "pyproject.toml",
    ]
    paths += sorted((ROOT / "src").rglob("*.py"))
    paths += [
        ROOT / "tests" / f"test_{name}.py"
        for name in (
            "evaluation",
            "splitting",
            "inspection",
            "features",
            "pca",
            "autoencoder",
            "scientific_audit",
        )
    ]
    return {str(path.relative_to(ROOT)): digest(path) for path in paths}


def binding_digest(bundle):
    return hashlib.sha256(
        json.dumps(bundle, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def runtime():
    import h5py
    import numpy as np
    import torch
    from threadpoolctl import threadpool_info, threadpool_limits

    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    controller = threadpool_limits(limits=1)
    pools = threadpool_info()
    if (
        torch.get_num_threads() != 1
        or torch.get_num_interop_threads() != 1
        or any(p["num_threads"] != 1 for p in pools)
    ):
        raise ValueError("effective CPU threads not one")
    output = io.StringIO()
    with redirect_stdout(output):
        np.show_config()
    record = dict(
        python=sys.version,
        executable=sys.executable,
        platform=platform.platform(),
        versions={
            name: importlib.metadata.version(name)
            for name in ("numpy", "scipy", "torch", "scikit-learn", "h5py", "pytest")
        },
        torch_build=torch.__config__.show(),
        numpy_build=output.getvalue(),
        hdf_build=h5py.version.info,
        threadpools=pools,
        torch_threads=torch.get_num_threads(),
        torch_interop=torch.get_num_interop_threads(),
        loader_workers=0,
    )
    return record, controller


def log(root, event, **fields):
    with (Path(root) / "ledger/events.jsonl").open("a") as stream:
        stream.write(
            json.dumps(dict(event=event, utc=utc(), **fields), allow_nan=False) + "\n"
        )
        stream.flush()
        os.fsync(stream.fileno())


def verify_binding(root):
    binding = json.loads(
        (Path(root) / "private/implementation-binding.json").read_text()
    )
    if (
        binding["bundle"] != behavioral_bundle()
        or not binding["generated_validation_passed"]
    ):
        raise ValueError("behavior/test/config/prompt changed or validation missing")
    return binding


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def acquire(root, protocol, config):
    """No automatic transport retry stack; every event request is journaled."""
    root = Path(root)
    opener = urllib.request.build_opener(NoRedirect)
    started = time.monotonic()
    wire, requests = 0, 0
    accepted = []
    old = json.loads(
        (
            ROOT / "results/tables/final/task0060-scientific-audit-summary.json"
        ).read_text()
    )
    for source in protocol["sources"]:
        file_started = time.monotonic()
        record_id = source["record_id"]
        prior = next(
            v
            for v in old["metadata_evidence"]
            if v["local_path"].endswith(f"zenodo-{record_id}.json")
        )
        prior_path = Path(prior["local_path"])
        if digest(prior_path) != prior["sha256"]:
            raise ValueError("historical metadata provenance mismatch")
        (root / "metadata" / f"task0060-{record_id}.json").write_bytes(
            prior_path.read_bytes()
        )
        log(root, "metadata_request", url=source["metadata_url"], source=source["role"])
        with opener.open(source["metadata_url"], timeout=30) as response:
            payload = response.read(100001)
            if len(payload) > 100000:
                raise ValueError("metadata transfer cap")
        (root / "metadata" / f"current-{record_id}.json").write_bytes(payload)
        metadata = json.loads(payload)
        files = [f for f in metadata["files"] if f["key"] == source["filename"]]
        if (
            len(files) != 1
            or files[0]["size"] != source["bytes"]
            or files[0]["checksum"] != source["checksum"]
            or int(metadata["id"]) != record_id
            or metadata["metadata"]["version"] != "v2"
        ):
            raise ValueError("publisher metadata contradiction")
        log(
            root,
            "metadata_accepted",
            source=source["role"],
            bytes=len(payload),
            sha256=hashlib.sha256(payload).hexdigest(),
        )
        target = root / "raw" / source["filename"]
        if target.exists():
            raise FileExistsError("unplanned existing raw file; inspect provenance")
        completed = False
        for attempt in (1, 2):
            part = root / "raw" / f"{source['filename']}.part-{attempt}"
            url = files[0]["links"]["self"]
            md5, sha = hashlib.md5(), hashlib.sha256()
            actual = 0
            try:
                for _ in range(4):
                    if (
                        requests >= 6
                        or wire >= 1024**3
                        or time.monotonic() - started >= 2700
                        or time.monotonic() - file_started >= 1200
                    ):
                        raise TimeoutError("event acquisition budget exhausted")
                    parsed = urllib.parse.urlparse(url)
                    if (
                        parsed.scheme != "https"
                        or parsed.hostname != "zenodo.org"
                        or source["filename"] not in parsed.path
                    ):
                        raise ValueError("unapproved event URL")
                    requests += 1
                    log(
                        root,
                        "event_request",
                        source=source["role"],
                        attempt=attempt,
                        request=requests,
                        url=url,
                        wire_bytes_so_far=wire,
                    )
                    try:
                        response = opener.open(url, timeout=30)
                        break
                    except urllib.error.HTTPError as error:
                        if error.code in (301, 302, 303, 307, 308):
                            newurl = urllib.parse.urljoin(
                                url, error.headers["Location"]
                            )
                            log(
                                root,
                                "event_redirect",
                                source=source["role"],
                                status=error.code,
                                from_url=url,
                                to_url=newurl,
                            )
                            url = newurl
                            error.close()
                            continue
                        raise
                else:
                    raise ValueError("redirect cap")
                with response, part.open("xb") as stream:
                    length = response.headers.get("Content-Length")
                    if length is not None and int(length) != source["bytes"]:
                        raise ValueError("event length contradiction")
                    while True:
                        remaining = min(source["bytes"] - actual, 1024**3 - wire)
                        if (
                            remaining < 0
                            or time.monotonic() - started >= 2700
                            or time.monotonic() - file_started >= 1200
                        ):
                            raise TimeoutError("event transfer budget")
                        block = response.read(min(1024 * 1024, remaining + 1))
                        if not block:
                            break
                        actual += len(block)
                        wire += len(block)
                        stream.write(block)
                        md5.update(block)
                        sha.update(block)
                        log(
                            root,
                            "event_bytes",
                            source=source["role"],
                            attempt=attempt,
                            partial_bytes=actual,
                            total_event_wire_bytes=wire,
                            event_requests=requests,
                        )
                        if actual > source["bytes"] or wire > 1024**3:
                            raise ValueError("event byte cap exceeded")
                if (
                    actual != source["bytes"]
                    or md5.hexdigest() != source["checksum"].split(":")[1]
                ):
                    raise ValueError("source length/checksum contradiction")
                local_md5 = hashlib.md5()
                local_sha = hashlib.sha256()
                with part.open("rb") as stored:
                    while block := stored.read(1024 * 1024):
                        local_md5.update(block)
                        local_sha.update(block)
                if (
                    part.stat().st_size != actual
                    or local_md5.digest() != md5.digest()
                    or local_sha.digest() != sha.digest()
                ):
                    raise ValueError("on-disk source integrity contradiction")
                os.rename(part, target)
                target.chmod(0o444)
                receipt = dict(
                    role=source["role"],
                    record_id=record_id,
                    filename=source["filename"],
                    bytes=actual,
                    md5=md5.hexdigest(),
                    sha256=sha.hexdigest(),
                    event_requests_cumulative=requests,
                    wire_bytes_cumulative=wire,
                    attempt=attempt,
                    inclusive_file_seconds=time.monotonic() - file_started,
                    metadata_sha256=digest(
                        root / "metadata" / f"current-{record_id}.json"
                    ),
                    on_disk_reverified=True,
                    local_verification_bytes=actual,
                )
                accepted.append(receipt)
                write_json(root / "private" / f"accepted-{record_id}.json", receipt)
                log(root, "source_accepted", **receipt)
                completed = True
                break
            except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
                log(
                    root,
                    "event_transfer_failed",
                    source=source["role"],
                    attempt=attempt,
                    partial_bytes=actual,
                    error=repr(error),
                )
                if isinstance(error, urllib.error.HTTPError) and error.code not in (
                    408,
                    429,
                    500,
                    502,
                    503,
                    504,
                ):
                    raise
                if attempt == 2:
                    raise
        if not completed:
            raise ValueError("source not accepted")
    write_json(
        root / "private/acquisition.json",
        dict(
            sources=accepted,
            event_wire_bytes=wire,
            event_transfer_requests=requests,
            accepted_bytes=sum(v["bytes"] for v in accepted),
            elapsed_seconds=time.monotonic() - started,
        ),
    )


def lifetime_rss_bytes():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform == "darwin" else value * 1024
