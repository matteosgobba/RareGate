"""Raw-file byte custody and HDF properties, with event-reading methods disabled."""

import hashlib
from contextlib import contextmanager

import h5py
import hdf5plugin

from latenttrigger.benchmarks import development_raw_protocol as p


def hash_raw(path, expected, audit, persist, poll):
    p.require(audit.get("raw_hash_attempts", 0) == 0, "One raw custody pass")
    p.require(
        path.absolute() == path.resolve()
        and path.stat().st_size == expected["size_bytes"],
        "Nonsymlink raw size",
    )
    audit.update(raw_hash_attempts=1, raw_hash_inflight=True, raw_hash_bytes=0)
    persist()
    sha = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(2**20):
            poll()
            sha.update(block)
            audit["raw_hash_bytes"] += len(block)
            p.require(
                audit["raw_hash_bytes"] <= expected["size_bytes"],
                "Changed raw size during hashing",
            )
            if audit["raw_hash_bytes"] % (64 * 2**20) == 0:
                persist()
    audit.update(raw_hash_passes=1, raw_hash_inflight=False, raw_sha256=sha.hexdigest())
    persist()
    p.require(
        audit["raw_hash_bytes"] == expected["size_bytes"]
        and sha.hexdigest() == expected["file_sha256"],
        "Raw full-byte identity",
    )


@contextmanager
def forbid_payload():
    names = ("__getitem__", "read_direct", "__array__", "astype", "iter_chunks")
    originals = {name: getattr(h5py.Dataset, name) for name in names}

    def refused(*args, **kwargs):
        raise PermissionError("Metadata resolver forbids HDF dataset values")

    for name in names:
        setattr(h5py.Dataset, name, refused)
    try:
        yield
    finally:
        for name, original in originals.items():
            setattr(h5py.Dataset, name, original)


def properties(handle, expected):
    for name in ("/df", "/df/block0_values"):
        p.require(
            isinstance(handle.get(name, getlink=True), h5py.HardLink),
            "No soft/external HDF links",
        )
    dataset = handle.get("/df/block0_values")
    p.require(
        h5py.h5o.get_info(handle.get("/df").id).rc == 1, "No ambiguous group aliases"
    )
    p.require(
        isinstance(dataset, h5py.Dataset) and h5py.h5o.get_info(dataset.id).rc == 1,
        "Unambiguous single dataset identity",
    )
    creation = dataset.id.get_create_plist()
    filters = []
    for i in range(creation.get_nfilters()):
        number, flags, parameters, name = creation.get_filter(i)
        filters.append(
            dict(
                id=number, flags=flags, parameters=list(parameters), name=name.decode()
            )
        )
    value = dict(
        shape=list(dataset.shape),
        dtype=str(dataset.dtype),
        chunks=list(dataset.chunks) if dataset.chunks else None,
        filters=filters,
    )
    p.require(value == expected, "Exact raw audit shape/dtype/chunks/filter pipeline")
    p.require(
        not dataset.is_virtual and creation.get_external_count() == 0,
        "No virtual/external dataset sources",
    )
    cache = dataset.id.get_access_plist().get_chunk_cache()
    p.require(cache == (521, 1048576, 0.75), "Effective fixed chunk cache")
    return dict(
        schema=value,
        effective_dataset_chunk_cache=dict(
            rdcc_nslots=cache[0], rdcc_nbytes=cache[1], rdcc_w0=cache[2]
        ),
        effective_file_cache=list(handle.id.get_access_plist().get_cache()),
        HDF_driver=handle.driver,
        event_dataset_values_read=0,
    )


def inspect(path, expected, audit, persist):
    p.require(audit.get("raw_HDF_open_attempts", 0) == 0, "One metadata HDF open")
    audit.update(raw_HDF_open_attempts=1, HDF_metadata_inflight=True)
    persist()
    identifier = None
    try:
        with forbid_payload(), h5py.File(path, "r", **p.CACHE) as handle:
            identifier = handle.id
            audit.update(raw_HDF_metadata_opens=1)
            persist()
            result = properties(handle, expected)
    finally:
        audit.update(HDF_handle_closed=identifier is not None and not identifier.valid)
        persist()
    p.require(not identifier.valid, "HDF handle released")
    audit.update(HDF_metadata_inflight=False)
    persist()
    return dict(
        **result,
        versions=dict(
            h5py=h5py.__version__,
            HDF5=h5py.version.hdf5_version,
            hdf5plugin=hdf5plugin.__version__
            if hasattr(hdf5plugin, "__version__")
            else p.dependencies()["packages"]["hdf5plugin"],
        ),
        decoder_threading=dict(
            BLOSC_NTHREADS_environment_requested="1",
            effective_decoder_threads="unknown_not_inferred_from_BLAS_OpenMP",
            plugin_build=hdf5plugin.get_config().build_config._asdict(),
            production_decoder_source_bound=False,
        ),
    )
