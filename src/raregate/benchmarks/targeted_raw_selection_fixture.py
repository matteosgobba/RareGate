"""Generated ten-file source metadata fixtures; no queue/physical engine invocation."""

import csv
import hashlib
import json

from raregate.benchmarks import targeted_raw_selection as s


def write(root, *, newline="\n"):
    def put(name, value):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((json.dumps(value, sort_keys=True, indent=2) + "\n").encode())
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def sha(name):
        return hashlib.sha256((root / name).read_bytes()).hexdigest()

    put(s.CONFIG, dict(task="0046", validation_owner="0046"))
    q = root / s.PROMPT
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text("Generated Task0046 source contract fixture, no operational source\n")
    identity = dict(
        task="0046",
        validation_owner="0046",
        scope="closed_Task0045_timing_metadata_synthetic_FIFO",
        assignment_contract_sha256="84f71df37c4b48801ce49f3c113b306c5bc90a0017e1b1e58da4f051071eb83d",
        config_sha256=sha(s.CONFIG),
        prompt_sha256=sha(s.PROMPT),
    )
    rows = []
    occupancies = []
    totals = {}
    for key in s.matrix():
        r = dict(zip(s.KEYS, key, strict=True))
        b = r["B"]
        if b == 1:
            hist = {1: 5000}
        elif b == 8:
            hist = {m: 1 for m in range(1, 8)}
            hist[4] += 1
            hist[8] = 621
        else:
            hist = {m: 1 for m in range(1, 17)}
            hist[b] = (5000 - 136) // b
        acc = dict(
            batches=0,
            events=0,
            busy_ns=0,
            modeled_rows=0,
            exact_batches=0,
            exact_events=0,
            exact_busy_ns=0,
            mapped_batches=0,
            mapped_events=0,
            mapped_busy_ns=0,
            anchor_minus_actual_rows=0,
            modeled_minus_actual_rows=0,
        )
        for m, count in sorted(hist.items()):
            k = s.lookup(b, m, r["mapping"])
            modeled = k if r["billing"] == "natural_anchor" else b
            busy = count * (
                k * 1000 + 100 if r["billing"] == "natural_anchor" else b * 1000
            )
            sb = k if (b, k) in ((32, 8), (128, 32)) else b
            o = dict(
                r,
                m=m,
                k=k,
                batches=count,
                events=count * m,
                busy_ns=busy,
                modeled_rows=count * modeled,
                exact_point=int(k == m),
                source_natural_actual_rows=k,
                source_natural_service_B=sb,
                source_control_actual_rows=b,
                source_control_service_B=b,
                k_minus_m=k - m,
                anchor_minus_actual_rows=(k - m) * count,
                modeled_minus_actual_rows=count * (modeled - m),
            )
            occupancies.append(o)
            for n in (
                "batches",
                "events",
                "busy_ns",
                "modeled_rows",
                "anchor_minus_actual_rows",
                "modeled_minus_actual_rows",
            ):
                acc[n] += o[n]
            for n in ("batches", "events", "busy_ns"):
                acc[("exact_" if k == m else "mapped_") + n] += o[n]
        row = dict(
            r,
            generated=5000,
            admitted=5000,
            overflow_dropped=0,
            completed=5000,
            pending=0,
            batches=acc["batches"],
            full_batches=hist[b],
            partial_batches=acc["batches"] - hist[b],
            busy_ns=acc["busy_ns"],
            modeled_row_work=acc["modeled_rows"],
            **{
                n: acc[n]
                for n in acc
                if n.startswith(("exact_", "mapped_")) or n.endswith("actual_rows")
            },
        )
        rows.append(row)
        t = totals.setdefault(
            r["mapping"] + "/" + r["billing"],
            {
                n: 0
                for n in (
                    "generated",
                    "completed",
                    "overflow_dropped",
                    "batches",
                    "busy_ns",
                    "mapped_batches",
                    "mapped_events",
                    "mapped_busy_ns",
                    "modeled_row_work",
                    "anchor_minus_actual_rows",
                    "modeled_minus_actual_rows",
                )
            },
        )
        for n in t:
            t[n] += row[n]
    for name, values in ((s.SCENARIOS, rows), (s.OCCUPANCIES, occupancies)):
        q = root / name
        q.parent.mkdir(parents=True, exist_ok=True)
        with q.open("x", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(values[0]), lineterminator=newline)
            w.writeheader()
            w.writerows(values)
    status = "parent_accepted_synthetic_occupancy_service_replay"
    common = dict(
        identity=identity,
        source_map={"inert/forbidden/raw.h5": "a" * 64},
        dependencies={"fixture": "only"},
    )
    plan = dict(common, fixture_only=False, validation_bootstrap=False)
    plan_sha = put(s.DIRECTORY + "/plan.json", plan)
    phases = []
    for phase in ("simulation", "reporting"):
        outputs = (
            {
                name: sha(path)
                for name, path in (
                    ("scenarios.csv", s.SCENARIOS),
                    ("occupancies.csv", s.OCCUPANCIES),
                )
            }
            if phase == "simulation"
            else {"summary.json": "b" * 64}
        )
        receipt = dict(
            common, status="body_complete_awaiting_exit", phase=phase, outputs=outputs
        )
        receipt_sha = put(s.DIRECTORY + "/" + phase + "/receipt.json", receipt)
        phases.append(
            dict(
                phase=phase,
                body_sha256=receipt_sha,
                dispatch=dict(
                    returncode=0,
                    child_reaped=True,
                    parent_confirms_normal_exit=True,
                    within_deadline=True,
                    parent_error=None,
                    overshoot_seconds=0,
                ),
            )
        )
    workflow = dict(
        common,
        status=status,
        fixture_only=False,
        plan_sha256=plan_sha,
        overshoot_seconds=0,
        sleep_assertion=dict(
            released=True, owned_assertion_absent=True, lifecycle=dict(reaped=True)
        ),
        phases=phases,
    )
    workflow_sha = put(s.DIRECTORY + "/workflow.json", workflow)
    put(
        s.DIRECTORY + "/parent-acceptance.json",
        dict(
            identity=identity,
            status=status,
            workflow_sha256=workflow_sha,
            plan_sha256=plan_sha,
        ),
    )
    put(
        s.SUMMARY,
        dict(
            identity=identity,
            status=status,
            operational_allowance_consumed=True,
            workflow_sha256=workflow_sha,
            execution_plan_sha256=plan_sha,
            audit_row_counts=dict(occupancies=len(occupancies)),
            totals=totals,
        ),
    )
    return {n: dict(bytes=(root / n).stat().st_size, sha256=sha(n)) for n in s.NAMES}
