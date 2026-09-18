"""Run the full pipeline: download, transform, and write outputs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from data_pipeline.pipeline import run

if __name__ == "__main__":
    outputs = run()
    for kind, path in outputs.items():
        print(f"wrote {kind}: {path}")
