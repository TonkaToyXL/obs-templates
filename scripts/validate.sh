#!/usr/bin/env bash
# Pre-publish safety scan — blocks packaging if personal paths or secrets are found.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES="$ROOT/templates"
DIST="$ROOT/dist"

FAIL=0

red() { printf '\033[31m%s\033[0m\n' "$1"; }
ok() { printf '  ✓ %s\n' "$1"; }

check_patterns() {
  local label="$1"
  local pattern="$2"
  shift 2
  local hits
  hits="$(rg -n --hidden -S "$pattern" "$@" "$TEMPLATES" "$DIST" 2>/dev/null || true)"
  if [[ -n "$hits" ]]; then
    red "FAIL: $label"
    echo "$hits"
    FAIL=1
  else
    ok "$label"
  fi
}

echo "Safety scan (shippable: templates/ + dist/)…"
echo

check_patterns "no home-directory paths" '/Users/[A-Za-z]|/home/[a-z]|C:\\\\Users\\\\'
check_patterns "no file:// URLs" 'file://'
check_patterns "no personal username paths" 'account-owner|account-owner'
check_patterns "no email addresses" '@gmail\.com|@[a-z0-9.-]+\.(com|io|net)'
check_patterns "no cloud-sync paths" 'CloudStorage|GoogleDrive|Dropbox'
check_patterns "no OBS config absolute paths" 'Library/Application Support/obs-studio' \
  --glob '!install.py' --glob '!Install.bat' --glob '!install.command'
check_patterns "no hardcoded WebSocket passwords" 'wsPassword:\s*["\x27][^"\x27]+["\x27]'
check_patterns "no API keys or tokens" 'api[_-]?key|secret[_-]?key|sk-[a-zA-Z0-9]{10,}'

echo
echo "Manifest checks…"

shopt -s nullglob
for dir in "$TEMPLATES"/*/; do
  id="$(basename "$dir")"
  [[ "$id" == _* ]] && continue

  manifest="$dir/manifest.json"
  readme="$dir/README.md"

  if [[ ! -f "$manifest" ]]; then
    red "FAIL: $id missing manifest.json"
    FAIL=1
    continue
  fi
  if [[ ! -f "$readme" ]]; then
    red "FAIL: $id missing README.md"
    FAIL=1
    continue
  fi
  for required in install.command Install.bat install.py "docs/install-guide.html"; do
    if [[ ! -f "$dir/$required" ]]; then
      red "FAIL: $id missing $required (run ./scripts/generate-installers.sh)"
      FAIL=1
    fi
  done

  if ! python3 - "$id" "$manifest" <<'PY'
import json, re, sys
folder_id, path = sys.argv[1], sys.argv[2]
m = json.load(open(path))
required = ["id", "name", "version", "description"]
for key in required:
    if not m.get(key):
        print(f"FAIL: {folder_id} manifest missing '{key}'")
        sys.exit(1)
if m["id"] != folder_id:
    print(f"FAIL: {folder_id} manifest id '{m['id']}' must match folder name")
    sys.exit(1)
if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", m["id"]):
    print(f"FAIL: {folder_id} id must be kebab-case")
    sys.exit(1)
if not re.fullmatch(r"\d+\.\d+\.\d+", m["version"]):
    print(f"FAIL: {folder_id} version must be semver (e.g. 1.0.0)")
    sys.exit(1)
print(f"  ✓ manifest: {folder_id} v{m['version']}")
PY
  then
    FAIL=1
  fi
done

echo
if [[ $FAIL -ne 0 ]]; then
  red "Validation failed — fix issues before publishing."
  exit 1
fi

ok "All checks passed — safe to package and push."
