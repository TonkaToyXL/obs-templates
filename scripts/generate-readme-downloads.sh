#!/usr/bin/env bash
# Regenerate the download table in README.md between marker comments.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export ROOT

python3 <<'PY'
import json
import glob
import os
from pathlib import Path

root = Path(os.environ["ROOT"])
templates = root / "templates"
dist = root / "dist"
rows = []

for manifest_path in sorted(templates.glob("*/manifest.json")):
    m = json.loads(manifest_path.read_text())
    tid = m["id"]
    version = m["version"]
    zip_name = f"{tid}-v{version}.zip"
    zip_path = dist / zip_name
    if not zip_path.exists():
        continue
    size_kb = zip_path.stat().st_size // 1024
    rows.append(
        f"| **{m['name']}** | {m['description']} | "
        f"[Download `{zip_name}`](./dist/{zip_name}) ({size_kb} KB) | "
        f"{m.get('obsMinVersion', '30+')} |"
    )

table = "\n".join(rows) if rows else "| _No packages yet — run `./scripts/package.sh`_ | | | |"

readme = (root / "README.md").read_text()
start = "<!-- DOWNLOADS:START -->"
end = "<!-- DOWNLOADS:END -->"
if start not in readme or end not in readme:
    raise SystemExit("README markers missing")

new_block = f"{start}\n{table}\n{end}"
import re
updated = re.sub(
    rf"{re.escape(start)}.*?{re.escape(end)}",
    new_block,
    readme,
    count=1,
    flags=re.DOTALL,
)
(root / "README.md").write_text(updated)
print("README download table updated")
PY
