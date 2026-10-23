"""Run usage_example.md literally against the official notebook (Step 4.1, the multi-day study call, is skipped).

Usage: python verification/run_usage_example.py [--label-style calendar|vendor] [--output-dir DIR]
"""
import argparse
import os
import re
import shutil
import sys
import time
import __future__
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "verification"))
from notebook_namespace import load_namespace  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--label-style", choices=("calendar", "vendor"), default=None)
parser.add_argument("--output-dir", default=None)
args = parser.parse_args()

os.chdir(ROOT)
started = time.time()
namespace = load_namespace(ROOT)
print(f"notebook definitions loaded in {time.time() - started:.1f}s", flush=True)

# Collect every python fence with the heading it sits under.
text = (ROOT / "usage_example.md").read_text(encoding="utf-8")
fences, heading, inside, buffer = [], "", False, []
for line in text.splitlines():
    if not inside and re.match(r"^#{2,4} ", line):
        heading = line
    if line.startswith("```"):
        if not inside and line.strip() == "```python":
            inside, buffer = True, []
        elif inside:
            fences.append((heading, "\n".join(buffer)))
            inside = False
        continue
    if inside:
        buffer.append(line)

# Names the caller may override once the fence that defines them has run.
overrides = {}
if args.label_style:
    overrides["FISCAL_LABEL_STYLE"] = args.label_style
if args.output_dir:
    overrides["SMOKE_OUTPUT_DIR"] = str(Path(args.output_dir).expanduser().resolve())

flags = __future__.annotations.compiler_flag
for number, (heading, source) in enumerate(fences, start=1):
    if "Step 4.1" in heading:
        print(f"----- fence {number} skipped (Step 4.1 is the multi-day study call)", flush=True)
        continue
    if "smoke_result = execute_study" in source:
        target = Path(namespace["SMOKE_OUTPUT_DIR"])
        if target.exists():
            shutil.rmtree(target)  # a fresh directory, so no stage is resumed from an old checkpoint
        print(f"----- smoke run into {target}", flush=True)
    print(f"----- fence {number}: {heading.strip('# *')}", flush=True)
    exec(compile(source, f"<usage fence {number}>", "exec", flags=flags, dont_inherit=True), namespace)
    for name, value in overrides.items():
        if name in namespace:
            namespace[name] = value
print(f"----- finished in {(time.time() - started) / 60:.1f} min", flush=True)
result = namespace["smoke_result"]
assert result["status"] == "completed", result["status"]
assert namespace["smoke_summary"]["study_status"] == "pipeline_verified_on_synthetic_data"
print("SMOKE OK", result["manifest_path"])
