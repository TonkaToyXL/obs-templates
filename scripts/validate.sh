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

check_paths() {
  local label="$1"
  local pattern="$2"
  shift 2
  local hits
  hits="$(rg -n --hidden -S "$pattern" "$@" 2>/dev/null || true)"
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
check_patterns "no personal dev paths" '00_ACTIVE|github-public-publish'
check_patterns "no email addresses" '@gmail\.com|@[a-z0-9.-]+\.(com|io|net)'
check_patterns "no cloud-sync paths" 'CloudStorage|GoogleDrive|Dropbox'
check_patterns "no OBS config absolute paths" 'Library/Application Support/obs-studio' \
  --glob '!install.py' --glob '!installer.py' --glob '!Install.bat' --glob '!install.command'
check_patterns "no hardcoded WebSocket passwords" 'wsPassword:\s*["\x27][^"\x27]+["\x27]|WS_PASS\s*=\s*os\.environ\.get\([^)]+,\s*["\x27][^"\x27]{6,}'
check_patterns "no API keys or tokens" 'api[_-]?key|secret[_-]?key|sk-[a-zA-Z0-9]{10,}'
check_patterns "no stream keys" 'live_[0-9]+_[a-zA-Z0-9]+'
check_patterns "no device-specific mic names in templates" 'Blue Nessie|AppleUSBAudioEngine' \
  --glob '!README.md' --glob '!FOR-US.md'

echo
echo "Scripts + docs scan…"
check_paths "no personal paths in scripts" 'account-owner|account-owner|tonka_assets' \
  "$ROOT/scripts" \
  --glob '!validate.sh' --glob '!install-local-default.py'
check_paths "no personal paths in root docs" 'account-owner|account-owner|tonka_assets|Blue Nessie|00_ACTIVE|github-public-publish' \
  "$ROOT/README.md" "$ROOT/FOR-US.md" "$ROOT/SECURITY.md" "$ROOT/STREAM.md"

echo
echo "Zip contents scan…"
for zip in "$DIST"/*.zip; do
  [[ -f "$zip" ]] || continue
  hits="$(unzip -p "$zip" 2>/dev/null | rg -n -i 'account-owner|account-owner|@gmail\.com|FhMd|tonka_assets|CloudStorage|Blue Nessie|LOCAL_AREA' || true)"
  if [[ -n "$hits" ]]; then
    red "FAIL: personal data in $(basename "$zip")"
    echo "$hits" | head -20
    FAIL=1
  else
    ok "zip clean: $(basename "$zip")"
  fi
done

echo
echo "Shared pack sync…"
"$ROOT/scripts/sync-shared.sh" >/dev/null
SHARED="$TEMPLATES/_shared"
if [[ -d "$SHARED" ]]; then
  shopt -s nullglob
  for dir in "$TEMPLATES"/*/; do
    id="$(basename "$dir")"
    [[ "$id" == _* ]] && continue
    [[ -f "$dir/manifest.json" ]] || continue
    for rel in bridge/orb-bridge.py bridge/start-bridge.sh bridge/start-bridge.bat overlays/privacy-blur.html; do
      if [[ -f "$SHARED/$rel" ]]; then
        if ! cmp -s "$SHARED/$rel" "$dir/$rel"; then
          red "FAIL: $id/$rel diverges from templates/_shared/$rel (run ./scripts/sync-shared.sh)"
          FAIL=1
        else
          ok "shared match: $id/$rel"
        fi
      fi
    done
  done
fi

echo
echo "Manifest + scene checks…"

if ! python3 "$ROOT/scripts/manifest_validate.py" "$TEMPLATES"; then
  FAIL=1
else
  shopt -s nullglob
  for dir in "$TEMPLATES"/*/; do
    id="$(basename "$dir")"
    [[ "$id" == _* ]] && continue
    [[ -f "$dir/manifest.json" ]] || continue
    version="$(python3 -c "import json; print(json.load(open('$dir/manifest.json'))['version'])")"
    ok "manifest: $id v$version"
  done
fi

echo
if [[ $FAIL -ne 0 ]]; then
  red "Validation failed — fix issues before publishing."
  exit 1
fi

ok "All checks passed — safe to package and push."
