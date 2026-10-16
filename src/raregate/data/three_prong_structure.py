"""Bounded HDF structure only: no dataset, axis, particle or label value reads."""


def inspect(path, *, boundary=lambda: None):
    import h5py

    rows, seen = [], set()
    relevant = {
        "CLASS",
        "VERSION",
        "pandas_type",
        "pandas_version",
        "ndim",
        "nblocks",
        "axis0_variety",
        "axis1_variety",
        "block0_items_variety",
        "encoding",
        "errors",
        "kind",
        "name",
        "transposed",
    }

    def attributes(obj):
        result = {}
        for key in sorted(relevant.intersection(obj.attrs)):
            aid = obj.attrs.get_id(key)
            dtype, shape = aid.dtype, aid.shape
            count = 1
            for value in shape:
                count *= value
            if (
                dtype.kind not in "biufSU"
                or shape != ()
                or count * dtype.itemsize > 512
            ):
                result[key] = dict(
                    status="skipped_non_scalar_or_unbounded",
                    dtype=str(dtype),
                    shape=list(shape),
                )
                continue
            value = obj.attrs[key]  # Structural attributes only, bounded before read.
            if hasattr(value, "item"):
                value = value.item()
            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="replace")
            result[key] = dict(status="bounded_structural_attribute", value=value)
        return result

    def visit(group, depth):
        boundary()
        if depth > 8 or len(group) > 64:
            raise ValueError("Bounded structural group/depth ceiling")
        for key in group:
            if len(rows) >= 64 or len(key.encode()) > 256:
                raise ValueError("Bounded structural node/name ceiling")
            path = group.name.rstrip("/") + "/" + key
            link = group.get(key, getlink=True)
            row = dict(path=path, link_type=type(link).__name__)
            rows.append(row)
            if not isinstance(link, h5py.HardLink):
                row["dereferenced"] = False
                continue
            obj = group[key]
            address = h5py.h5o.get_info(obj.id).addr
            if address in seen:
                row["status"] = "repeated_hard_link_not_traversed"
                continue
            seen.add(address)
            row["attributes"] = attributes(obj)
            if isinstance(obj, h5py.Group):
                row["kind"] = "group"
                visit(obj, depth + 1)
            elif isinstance(obj, h5py.Dataset):
                dcpl = obj.id.get_create_plist()
                if dcpl.get_nfilters() > 8:
                    raise ValueError("Bounded HDF filter count")
                filters = []
                for i in range(dcpl.get_nfilters()):
                    code, flags, values, name = dcpl.get_filter(i)
                    if len(values) > 32 or len(name) > 512:
                        raise ValueError("Bounded filter metadata")
                    filters.append(
                        dict(
                            id=code,
                            flags=flags,
                            parameters=list(values),
                            name=name.decode(errors="replace"),
                        )
                    )
                row.update(
                    kind="dataset",
                    shape=list(obj.shape),
                    dtype=str(obj.dtype),
                    chunks=list(obj.chunks) if obj.chunks else None,
                    filters=filters,
                    virtual=obj.is_virtual,
                    external=bool(obj.external),
                )
            else:
                row["kind"] = "unsupported_object"

    try:
        with h5py.File(path, "r") as handle:
            root_attributes = attributes(handle)
            seen.add(h5py.h5o.get_info(handle.id).addr)
            visit(handle, 0)
        bypath = {r["path"]: r for r in rows}
        expected = {"/df/block0_values", "/df/block0_items", "/df/axis0", "/df/axis1"}
        datasets = {r["path"] for r in rows if r.get("kind") == "dataset"}
        values = bypath.get("/df/block0_values", {})
        shape = values.get("shape", [])
        compatible = (
            datasets == expected
            and {r["path"] for r in rows} == expected | {"/df"}
            and len(shape) == 2
            and shape[0] == 100000
            and shape[1] in (2100, 2101)
            and values.get("dtype") == "float64"
            and all(
                bypath[key]["link_type"] == "HardLink"
                and not bypath[key]["virtual"]
                and not bypath[key]["external"]
                for key in expected
            )
            and all(
                bypath[key]["shape"] == [shape[1]]
                and bypath[key]["dtype"].startswith(("int", "uint"))
                for key in ("/df/block0_items", "/df/axis0")
            )
            and bypath["/df/axis1"]["shape"] == [100000]
            and bypath["/df/axis1"]["dtype"].startswith(("int", "uint"))
        )
        return dict(
            status="compatible_looking_structural_metadata_only"
            if compatible
            else "unsupported_structure",
            root_attributes=root_attributes,
            nodes=rows,
            dataset_value_reads=0,
            numerical_custody_passed=False,
            caveat="Shapes/dtypes do not verify axis order, labels, padding, valid events, uniqueness, overlap or scientific compatibility",
        )
    except Exception as error:
        # Guard/deadline failures must propagate, never be relabeled structural errors.
        from raregate.evaluation.guard import GuardError

        if isinstance(error, (GuardError, TimeoutError)):
            raise
        return dict(
            status="inspection_error",
            error=f"{type(error).__name__}: {error}",
            nodes=rows,
            dataset_value_reads=0,
            numerical_custody_passed=False,
        )
