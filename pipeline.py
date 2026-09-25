"""Run the whole pipeline, from the project folder:

    uv run python pipeline.py

Each stage is a script in scripts/, run in order in a fresh Python process. If a stage fails, the run stops there and
says which stage it was. Run it twice: the second run must make the same tables as the first.
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
STAGES = ["scripts/clean.py", "scripts/report.py"]

for stage in STAGES:
    print(f"\n== {stage}", flush=True)
    result = subprocess.run([sys.executable, stage], cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"\n== pipeline STOPPED at {stage}. Nothing after it ran.", flush=True)
        sys.exit(1)
print("\n== pipeline finished")
