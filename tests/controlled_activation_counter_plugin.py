"""Only new research helper counters; unrelated historical tests are excluded."""

import json
import os
import sys
from pathlib import Path


def pytest_sessionfinish(session, exitstatus):
    module = sys.modules.get("latenttrigger.research.controlled_activation.models")
    if module is not None and os.environ.get("TASK0035_COUNTER_OUTPUT"):
        Path(os.environ["TASK0035_COUNTER_OUTPUT"]).write_text(
            json.dumps(
                dict(
                    exit_status=exitstatus,
                    scope="this pytest process; instrumented new research helpers only; excludes unrelated historical models and native subprocess",
                    counters=dict(module.COUNTERS),
                ),
                indent=2,
            )
            + "\n"
        )
