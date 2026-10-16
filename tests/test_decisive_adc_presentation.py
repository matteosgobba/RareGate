"""Post-unblinding presentation-only checks using small generated scalar tables."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    spec = importlib.util.spec_from_file_location(
        "adc_scalar_presentation", ROOT / "scripts/present_decisive_adc_results.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_presentation_import_is_inactive():
    module = load()
    assert callable(module.draw) and module.ARMS[0] == "compactAE"


def test_generated_scalar_figures_and_closed_plot_resources(tmp_path):
    import matplotlib.pyplot as plt

    module = load()
    arms = module.ARMS
    summary = dict(
        inference_family=[
            dict(
                kind="efficiency",
                arm=a,
                signal=s,
                alpha=0.01,
                point=0.2,
                lower=0.1,
                upper=0.3,
            )
            for a in arms
            for s in module.SIGNALS
        ],
        cost_rules={
            name: dict(ratios=[0.9] * 8)
            for name in (
                "compactAE_over_referenceAE",
                "PCA3_over_compactAE",
                "regularizedMahalanobis_over_compactAE",
            )
        },
    )
    points = [
        dict(scope="stream", arm=a, signal=s, alpha=0.01, efficiency=0.2)
        for a in arms
        for s in module.SIGNALS
    ]
    costs = [
        dict(
            scope="measured_stream_cell",
            arm=a,
            batch=32,
            boundary="joint",
            repetition=rep,
            mean_ns=300000.0,
        )
        for a in arms
        for rep in range(8)
    ]
    module.draw(summary, points, costs, tmp_path)
    assert len(list(tmp_path.glob("*.png"))) == 3
    assert all(p.stat().st_size > 10000 for p in tmp_path.glob("*.png"))
    assert plt.get_fignums() == []
