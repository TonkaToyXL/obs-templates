#!/usr/bin/env bash
# Pre-publish safety scan — blocks packaging if personal paths or secrets are found.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES="$ROOT/templates"
DIST="$ROOT/dist"

FAIL=0

load_private_patterns() {
  local pattern_file="${OBS_PRIVATE_PATTERNS_FILE:-$ROOT/scripts/private-patterns.local}"
  local combined="${OBS_PRIVATE_PATTERN_REGEX:-}"
  local pattern

  if [[ -f "$pattern_file" ]]; then
    while IFS= read -r pattern || [[ -n "$pattern" ]]; do
      [[ -z "$pattern" || "$pattern" == \#* ]] && continue
      if [[ -n "$combined" ]]; then
        combined="$combined|($pattern)"
      else
        combined="($pattern)"
      fi
    done < "$pattern_file"
  fi

  printf '%s' "$combined"
}

PRIVATE_PATTERN_REGEX="$(load_private_patterns)"
PRIVATE_PATTERN_VALID=1

if [[ -n "$PRIVATE_PATTERN_REGEX" ]]; then
  regex_status=0
  printf '' | rg -q "$PRIVATE_PATTERN_REGEX" 2>/dev/null || regex_status=$?
  if (( regex_status >= 2 )); then
    printf '\033[31m%s\033[0m\n' "FAIL: invalid locally configured private-marker regex"
    FAIL=1
    PRIVATE_PATTERN_VALID=0
  fi
fi

red() { printf '\033[31m%s\033[0m\n' "$1"; }
ok() { printf '  ✓ %s\n' "$1"; }

check_patterns() {
  local label="$1"
  local pattern="$2"
  shift 2
  local hits
  local status=0
  hits="$(rg -n --hidden -S "$pattern" "$@" "$TEMPLATES" "$DIST" 2>&1)" || status=$?
  if (( status == 0 )); then
    red "FAIL: $label"
    echo "$hits"
    FAIL=1
  elif (( status == 1 )); then
    ok "$label"
  else
    red "FAIL: $label (scanner error)"
    echo "$hits"
    FAIL=1
  fi
}

check_paths() {
  local label="$1"
  local pattern="$2"
  shift 2
  local hits
  local status=0
  hits="$(rg -n --hidden -S "$pattern" "$@" 2>&1)" || status=$?
  if (( status == 0 )); then
    red "FAIL: $label"
    echo "$hits"
    FAIL=1
  elif (( status == 1 )); then
    ok "$label"
  else
    red "FAIL: $label (scanner error)"
    echo "$hits"
    FAIL=1
  fi
}

echo "Safety scan (shippable: templates/ + dist/)…"
echo

check_patterns "no home-directory paths" '/Users/[A-Za-z]|/home/[a-z]|C:\\\\Users\\\\'
check_patterns "no file:// URLs" 'file://'
check_patterns "no email addresses" '@gmail\.com|@[a-z0-9.-]+\.(com|io|net)'
check_patterns "no cloud-sync paths" 'CloudStorage|GoogleDrive|Dropbox'
check_patterns "no OBS config absolute paths" 'Library/Application Support/obs-studio' \
  --glob '!install.py' --glob '!installer.py' --glob '!Install.bat' --glob '!install.command'
check_patterns "no hardcoded WebSocket passwords" 'wsPassword:\s*["\x27][^"\x27]+["\x27]|WS_PASS\s*=\s*os\.environ\.get\([^)]+,\s*["\x27][^"\x27]{6,}'
check_patterns "no API keys or tokens" 'api[_-]?key|secret[_-]?key|sk-[a-zA-Z0-9]{10,}'
check_patterns "no stream keys" 'live_[0-9]+_[a-zA-Z0-9]+'
check_patterns "no device-specific mic names in templates" 'AppleUSBAudioEngine' \
  --glob '!README.md' --glob '!FOR-US.md'
if [[ -n "$PRIVATE_PATTERN_REGEX" && $PRIVATE_PATTERN_VALID -eq 1 ]]; then
  check_patterns "no locally configured private markers" "$PRIVATE_PATTERN_REGEX"
fi

echo
echo "Scripts + docs scan…"
check_paths "no personal paths in scripts" '/Users/[A-Za-z]|/home/[a-z]|C:\\\\Users\\\\|CloudStorage|GoogleDrive|Dropbox' \
  "$ROOT/scripts" \
  --glob '!validate.sh' --glob '!install-local-default.py' --glob '!private-patterns.local'
check_paths "no personal paths in root docs" '/Users/[A-Za-z]|/home/[a-z]|C:\\\\Users\\\\|CloudStorage|GoogleDrive|Dropbox' \
  "$ROOT/README.md" "$ROOT/FOR-US.md" "$ROOT/SECURITY.md" "$ROOT/STREAM.md"
if [[ -n "$PRIVATE_PATTERN_REGEX" && $PRIVATE_PATTERN_VALID -eq 1 ]]; then
  check_paths "no locally configured private markers in scripts" "$PRIVATE_PATTERN_REGEX" \
    "$ROOT/scripts" --glob '!private-patterns.local'
  check_paths "no locally configured private markers in root docs" "$PRIVATE_PATTERN_REGEX" \
    "$ROOT/README.md" "$ROOT/FOR-US.md" "$ROOT/SECURITY.md" "$ROOT/STREAM.md"
fi

echo
echo "Zip contents scan…"
ZIP_PATTERN='/Users/[A-Za-z]|/home/[a-z]|C:\\\\Users\\\\|file://|@gmail\.com|@[a-z0-9.-]+\.(com|io|net)|CloudStorage|GoogleDrive|Dropbox|wsPassword:[[:space:]]*["\x27][^"\x27]+["\x27]|WS_PASS[[:space:]]*=[[:space:]]*os\.environ\.get\([^)]+,[[:space:]]*["\x27][^"\x27]{6,}|api[_-]?key|secret[_-]?key|sk-[a-zA-Z0-9]{10,}|live_[0-9]+_[a-zA-Z0-9]+|AppleUSBAudioEngine'
if [[ -n "$PRIVATE_PATTERN_REGEX" && $PRIVATE_PATTERN_VALID -eq 1 ]]; then
  ZIP_PATTERN="$ZIP_PATTERN|$PRIVATE_PATTERN_REGEX"
fi
for zip in "$DIST"/*.zip; do
  [[ -f "$zip" ]] || continue
  if ! unzip -tqq "$zip" >/dev/null 2>&1; then
    red "FAIL: unreadable zip: $(basename "$zip")"
    FAIL=1
    continue
  fi

  content_status=0
  content_hits="$(unzip -p "$zip" | rg -a -n -i "$ZIP_PATTERN")" || content_status=$?
  name_status=0
  name_hits="$(unzip -Z1 "$zip" | rg -n -i "$ZIP_PATTERN")" || name_status=$?

  if (( content_status >= 2 || name_status >= 2 )); then
    red "FAIL: archive scanner error in $(basename "$zip")"
    [[ -n "$content_hits" ]] && echo "$content_hits"
    [[ -n "$name_hits" ]] && echo "$name_hits"
    FAIL=1
  elif [[ -n "$content_hits" || -n "$name_hits" ]]; then
    red "FAIL: personal data in $(basename "$zip")"
    [[ -n "$name_hits" ]] && printf 'entry: %s\n' "$name_hits"
    [[ -n "$content_hits" ]] && echo "$content_hits" | head -20
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
