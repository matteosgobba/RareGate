"""Fixed admission, aggregate boundary and lifecycle fixtures; no operational I/O."""

import pytest

from latenttrigger.benchmarks import prepared_service_protocol as p
from latenttrigger.benchmarks import prepared_service_runtime as rt
from latenttrigger.benchmarks.guard import NATIVE_METHOD, PRESSURE_METHOD
from latenttrigger.benchmarks.prepared_service_native import reserve
from latenttrigger.benchmarks.prepared_service_reporting import validate


def sample():
    return dict(
        peak_rss_bytes=10**7,
        native_heap_reserved_bytes=10**7,
        native_heap_in_use_bytes=10**6,
        workspace_method=NATIVE_METHOD,
        pressure_dispatch_flags=2,
        pressure_errno=None,
        pressure_method=PRESSURE_METHOD,
    )


@pytest.mark.parametrize("failure", ("RSS", "native", "primary", "critical", "clock"))
def test_resource_continuous_veto(tmp_path, failure):
    row = sample()
    now = [1.0]
    guard = rt.ServiceGuard(10, probe=lambda: row, clock=lambda: now[0], notify=False)
    guard.check()
    if failure == "RSS":
        row["peak_rss_bytes"] = 2**30 + 1
    if failure == "native":
        row["native_heap_reserved_bytes"] = 512 * 2**20 + 1
    if failure == "primary":
        row["workspace_method"] = "unverified"
    if failure == "critical":
        row["pressure_dispatch_flags"] = 4
    if failure == "clock":
        now[0] = 20  # simulated suspension; ordinary timer is irrelevant
    with pytest.raises(rt.GuardError):
        guard.check()


def test_warn_and_unavailable_pressure_disclosed():
    row = sample()
    guard = rt.ServiceGuard(10, probe=lambda: row, clock=lambda: 1, notify=False)
    guard.check()
    row.update(pressure_dispatch_flags=None, pressure_errno=5)
    guard.check()
    assert guard.report()["pressure_counts"]["WARN"] == 1
    assert guard.report()["pressure_counts"]["unknown"] == 1


@pytest.mark.parametrize(
    "name",
    (
        "event_features.npy",
        "scores.npy",
        "split_codes.npy",
        "fingerprints.npy",
        "particles.npy",
        "signal.h5",
        "model.pt",
        "old-receipt.json",
    ),
)
def test_narrow_reader_and_aggregate_boundary(tmp_path, name):
    root = tmp_path / "root"
    owned = root / "results/task0038/repetition1"
    for folder in ("data", "results", "artifacts", "sources"):
        with pytest.raises(PermissionError):
            rt.check_access(
                root, owned, set(), "open", (str(root / folder / name), "r", 0)
            )
    if name.endswith(".npy"):
        with pytest.raises(PermissionError):
            rt.check_access(root, owned, set(), "open", (str(owned / name), "r", 0))
    rt.check_access(root, owned, set(), "open", (str(owned / "aggregate.json"), "r", 0))


def test_allowed_prepared_and_forbidden_writes(tmp_path):
    root = tmp_path / "root"
    owned = root / "results/task0038/repetition1"
    source = root / "results/prepared/input.npy"
    rt.check_access(root, owned, {source}, "open", (str(source), "r", 0))
    with pytest.raises(PermissionError):
        rt.check_access(root, owned, {source}, "open", (str(source), "w", 0))
    for e in ("subprocess.Popen", "socket.connect", "os.system"):
        with pytest.raises(PermissionError):
            rt.check_access(root, owned, set(), e, ())


def test_atomic_one_winner_preserves_anchor(tmp_path, monkeypatch):
    monkeypatch.setattr(p, "ROOT", tmp_path)
    base = tmp_path / p.OUTPUT / "abc"
    base.mkdir(parents=True)
    plan = dict(prompt_sha256="1" * 64)
    p.durable_json(base / "plan.json", plan)
    reserve(base, plan)
    before = (tmp_path / p.OUTPUT / "attempt.json").read_bytes()
    with pytest.raises(FileExistsError):
        reserve(base, plan)
    assert (tmp_path / p.OUTPUT / "attempt.json").read_bytes() == before


def aggregate():
    rows = []
    for c in ("pca-v1", "compact-autoencoder-v2"):
        for b, m in p.CASES:
            for s in ("natural", "padded"):
                rows.append(
                    dict(
                        candidate=c,
                        repetition=1,
                        B=b,
                        m=m,
                        strategy=s,
                        count=2,
                        min_ns=1,
                        p50_ns=2,
                        p95_ns=3,
                        p99_ns=4,
                        max_ns=5,
                        executed_shape_rows=m if s == "natural" else b,
                    )
                )
    return dict(
        cells=rows,
        synthetic_only=True,
        chronology=[{}] * 136,
        paired=[{}] * 34,
        gates=[
            dict(
                before=dict(status="passed", mismatches_per_threshold=[0] * 4),
                after=dict(status="passed", mismatches_per_threshold=[0] * 4),
            )
        ],
    )


@pytest.mark.parametrize(
    "failure",
    ("missing", "duplicate", "count", "shape", "prepost", "threshold", "chronology"),
)
def test_incomplete_aggregate_rejected(failure):
    value = aggregate()
    validate(value)
    if failure == "missing":
        value["cells"].pop()
    if failure == "duplicate":
        value["cells"][-1] = value["cells"][0]
    if failure == "count":
        value["cells"][0]["count"] = 50
    if failure == "shape":
        value["cells"][0]["executed_shape_rows"] = 8
    if failure == "prepost":
        value["gates"][0]["after"]["status"] = "failed"
    if failure == "threshold":
        for key in ("before", "after"):
            value["gates"][0][key]["mismatches_per_threshold"] = [1] * 4
    if failure == "chronology":
        value["chronology"].pop()
    with pytest.raises(ValueError):
        validate(value)


@pytest.mark.parametrize(
    "failure", ("exit", "reap", "deadline", "body", "resource", "cleanup", "identity")
)
def test_parent_rejects_complete_body_without_lifecycle(tmp_path, monkeypatch, failure):
    monkeypatch.setattr(p, "source_map", lambda: {})
    monkeypatch.setattr(p, "dependencies", lambda: {})
    grant = dict(phase="probe", source_map={}, dependencies={})
    p.durable_json(tmp_path / "grant.json", grant)
    p.durable_json(tmp_path / "probe.json", {})
    body = dict(
        status="body_complete_awaiting_exit",
        grant_sha256=p.file_hash(tmp_path / "grant.json"),
        source_map={},
        dependencies={},
        resources=dict(
            latched_error=None,
            owned_thread_alive=False,
            peak_rss_bytes=1,
            native_heap_reserved_bytes=1,
        ),
        outputs={"probe.json": p.file_hash(tmp_path / "probe.json")},
        cleanup_seconds=0,
        monitor_closed_continuous=1,
    )
    dispatch = dict(
        returncode=0,
        parent_confirms_normal_exit=True,
        child_reaped=True,
        within_deadline=True,
        parent_error=None,
        end_continuous=2,
    )
    assert rt.accept(body, dispatch, grant, tmp_path, lambda: 2, 10)[
        "normal_exit_reaped"
    ]
    if failure == "exit":
        dispatch["returncode"] = -15
    if failure == "reap":
        dispatch["child_reaped"] = False
    if failure == "deadline":
        dispatch["within_deadline"] = False
    if failure == "body":
        body["status"] = "completed"
    if failure == "resource":
        body["resources"]["native_heap_reserved_bytes"] = 2**30
    if failure == "cleanup":
        body["cleanup_seconds"] = 3
    if failure == "identity":
        p.durable_json(tmp_path / "probe.json", dict(changed=True))
    with pytest.raises(ValueError):
        rt.accept(body, dispatch, grant, tmp_path, lambda: 2, 10)


def test_storage_caps_and_no_symlinks(tmp_path):
    log = tmp_path / "worker.log"
    log.write_bytes(b"x" * (2**20 + 1))
    with pytest.raises(ValueError):
        rt.storage(tmp_path)
    log.unlink()
    (tmp_path / "link").symlink_to(tmp_path)
    with pytest.raises(ValueError):
        rt.storage(tmp_path)


def test_duplicate_metadata_key(tmp_path):
    path = tmp_path / "fixture.json"
    path.write_text('{"a":1,"a":2}')
    with pytest.raises(ValueError):
        p.read(path)
