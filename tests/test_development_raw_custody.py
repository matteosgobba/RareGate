"""Small synthetic text/header bindings; operational arrays/providers never opened."""

import copy
import hashlib
import json

import numpy as np
import pytest

from latenttrigger.benchmarks import development_raw_protocol as p


def fixtures(root, monkeypatch):
    spec = copy.deepcopy(p.load())
    for key, dtype, shape in (
        ("membership", "<i8", (6999,)),
        ("golden", "<f4", (1024, 8)),
    ):
        path = root / spec[key]["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        values = (
            np.arange(6999, dtype=dtype)
            if key == "membership"
            else np.zeros(shape, dtype=dtype)
        )
        np.save(path, values, allow_pickle=False)
        spec[key]["file_sha256"] = p.file_hash(path)
        if key == "membership":
            spec[key]["selected_sha256"] = hashlib.sha256(
                values[:1024].tobytes()
            ).hexdigest()
        else:
            spec[key]["payload_sha256"] = hashlib.sha256(values.tobytes()).hexdigest()
    path = root / p.RAW
    path.parent.mkdir(parents=True)
    path.write_bytes(b"owned synthetic raw custody, no HDF payload")
    spec["raw"]["size_bytes"] = path.stat().st_size
    spec["raw"]["file_sha256"] = p.file_hash(path)
    integrity = dict(
        file_size=spec["raw"]["size_bytes"], sha256=spec["raw"]["file_sha256"]
    )

    def write(name, value):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) + "\n")

    config = dict(
        source_integrity=integrity,
        split=dict(
            protocol="lhco-rd-v1",
            seed=1729,
            counts=dict(dev_train_background=6999, train_background=699957),
            development_subset=dict(protocol="lhco-rd-dev-v1", fraction=0.01),
        ),
        analysis_provenance=dict(split_array_sha256={"train_background.npy": "1" * 64}),
    )
    write(spec["transform_config"], config)
    config_hash = p.file_hash(root / spec["transform_config"])
    write(spec["lineage"]["dev_configuration"], config)
    science = dict(
        scope="dev",
        counts=dict(train_background=6999, test_background=0, test_signal=0),
        config_sha256=config_hash,
        files={"configuration.json": dict(sha256=config_hash)},
        split_identity=dict(
            array_sha256={
                "dev_train_background.npy": spec["membership"]["file_sha256"],
                "train_background.npy": "1" * 64,
            },
            development_subset=config["split"]["development_subset"],
        ),
        source_integrity=integrity,
    )
    science["split_identity_sha256"] = p.digest(science["split_identity"])
    spec["lineage"]["dev_scientific_sha256"] = p.digest(science)
    write(
        spec["lineage"]["dev_manifest"],
        dict(scientific=science, scientific_sha256=p.digest(science)),
    )
    write(
        spec["lineage"]["split_manifest"],
        dict(
            artifacts={
                "dev_train_background.npy": dict(
                    sha256=spec["membership"]["file_sha256"]
                ),
                "train_background.npy": dict(sha256="1" * 64),
            },
            counts=config["split"]["counts"],
            development_subset=config["split"]["development_subset"],
            protocol="lhco-rd-v1",
            seed=1729,
            source_integrity=integrity,
        ),
    )
    population = dict(
        split="train_background",
        dev_only=True,
        allow_test=False,
        include_labels=False,
        status="completed",
        rows=1024,
        unique_rows=1024,
        ids_sha256=spec["membership"]["selected_sha256"],
    )
    write(
        spec["lineage"]["prepare_receipt"],
        dict(status="completed", access_audit=dict(population=population)),
    )
    write(
        spec["lineage"]["prepared"],
        dict(
            source_ids_bytes_sha256=spec["membership"]["selected_sha256"],
            strict_source_order=True,
            manifest_scientific_sha256=spec["lineage"]["dev_scientific_sha256"],
            input_file_sha256=spec["golden"]["file_sha256"],
            input_bytes_sha256=spec["golden"]["payload_sha256"],
        ),
    )
    write(
        spec["lineage"]["acquisition"],
        dict(
            sha256=spec["raw"]["file_sha256"],
            source=dict(record_id=6466204, version="v5"),
            verified_checksum=spec["raw"]["publisher_md5"],
        ),
    )
    write(
        spec["lineage"]["raw_audit"],
        dict(datasets={"df/block0_values": spec["raw"]["audit_schema"]}),
    )
    names = [v for k, v in spec["lineage"].items() if k != "dev_scientific_sha256"] + [
        spec["transform_config"]
    ]
    spec["byte_pins"] = {v: p.file_hash(root / v) for v in names}
    monkeypatch.setattr(p, "load", lambda *args: spec)
    monkeypatch.setattr(
        np,
        "load",
        lambda *args, **kw: pytest.fail(
            "Custody must not numerically load ID/golden/other arrays"
        ),
    )
    return spec


@pytest.mark.parametrize(
    "failure",
    (
        "role",
        "count",
        "ordering",
        "golden_relation",
        "split_hash",
        "scientific",
        "altered",
        "symlink",
    ),
)
def test_lineage_independent_of_filename_without_numeric_reads(
    tmp_path, monkeypatch, failure
):
    spec = fixtures(tmp_path, monkeypatch)
    assert p.custody(tmp_path)["numerical_ID_loads"] == 0
    name = spec["lineage"]["prepare_receipt"]
    document = p.read(tmp_path / name)
    if failure == "role":
        document["access_audit"]["population"]["split"] = "test_background"
    if failure == "count":
        document["access_audit"]["population"]["rows"] = 1023
    if failure == "ordering":
        name = spec["lineage"]["prepared"]
        document = p.read(tmp_path / name)
        document["strict_source_order"] = False
    if failure == "golden_relation":
        name = spec["lineage"]["prepared"]
        document = p.read(tmp_path / name)
        document["input_file_sha256"] = "0" * 64
    if failure == "split_hash":
        name = spec["lineage"]["split_manifest"]
        document = p.read(tmp_path / name)
        document["artifacts"]["dev_train_background.npy"]["sha256"] = "0" * 64
    if failure == "scientific":
        name = spec["lineage"]["dev_manifest"]
        document = p.read(tmp_path / name)
        document["scientific_sha256"] = "0" * 64
    if failure in ("altered", "symlink"):
        path = tmp_path / spec["membership"]["path"]
        if failure == "altered":
            path.write_bytes(path.read_bytes()[:-1] + b"x")
        else:
            other = tmp_path / "fixture.npy"
            path.rename(other)
            path.symlink_to(other)
    else:
        (tmp_path / name).write_text(json.dumps(document) + "\n")
        spec["byte_pins"][name] = p.file_hash(tmp_path / name)
    with pytest.raises(ValueError):
        p.custody(tmp_path)


@pytest.mark.parametrize(
    "key", ("membership", "raw", "golden", "future", "resolver_limits", "unknown")
)
def test_strict_config_cannot_grant_payload_or_other_roles(tmp_path, key):
    spec = p.load()
    spec[key] = None
    path = tmp_path / p.CONFIG
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(spec))
    with pytest.raises(ValueError):
        p.load(tmp_path)


def test_header_wrong_dtype_shape_fortran_and_pickle(tmp_path):
    for values in (
        np.zeros(6999, dtype="<f8"),
        np.zeros((6999, 1), dtype="<i8"),
        np.array([object()], dtype=object),
    ):
        path = tmp_path / "fixture.npy"
        np.save(path, values)
        with pytest.raises(ValueError):
            p.header(path, [6999], "<i8", 56120)
