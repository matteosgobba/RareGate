# Installation and workflow

Use Python 3.11 or 3.12 and a virtual environment. The core package depends on
NumPy, scikit-learn and PyTorch. Optional extras add HDF5 support, Matplotlib,
pytest and Ruff. A CPU is sufficient for the examples and numerical tests.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,data,analysis]"
python scripts/smoke_test.py
```

On Windows use `.venv\Scripts\activate`. For CPU-only Linux, install the CPU
PyTorch wheel before the editable package:

```bash
python -m pip install "torch>=2.6,<3" --index-url https://download.pytorch.org/whl/cpu
```

## Package structure

`raregate.data` handles verified sources, event representations and preprocessing;
`raregate.models` and `raregate.training` provide background reconstruction models;
`raregate.evaluation` covers score metrics and threshold rules. The ADC-specific
implementation is in `raregate.research.decisive_adc`. Benchmark, simulation and
streaming modules contain the corresponding research utilities.

For example, the ADC model interface accepts standardized FP32 arrays with twelve
columns:

```python
import numpy as np
from raregate.research.decisive_adc import models

model = models.ADCNet("compactAE", seed=1729)
features = np.zeros((32, 12), dtype=np.float32)
scores = models.public_score(model, features)
assert scores.shape == (32,)
```

This example uses an untrained model to illustrate the interface. Scientific
results require fitted weights and the matching training-derived preprocessing.
Raw inputs, processed arrays and most trained models are not distributed with
the repository. The [data guide](data-preparation.md) and
[experiment design](experiment-design.md) provide the definitions needed for an
independent reproduction; aggregate result tables alone cannot reproduce fits.

## LHCO inputs

The package also supports the corrected LHC Olympics R&D particle file from
[Zenodo v5](https://doi.org/10.5281/zenodo.6466204). The download interface verifies
publisher size/checksum and stores the payload locally:

```bash
python -m raregate.data.acquisition --help
python -m raregate.data.acquisition
python -m raregate.data.acquisition --verify-only
```

The file is about 2.9 GB. Its Blosc-compressed data require the `data` extra,
including hdf5plugin. LHCO's ragged particle/eight-feature representation is
separate from the ADC twelve-feature representation.

## Development checks

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest
```

Tests use generated inputs; they do not reproduce the scientific experiment.
Keep datasets, caches, temporary outputs and fitted weights outside version
control. When extending the analysis, preserve split boundaries and fit all
learned transformations on training data only.
