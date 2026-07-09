#!/usr/bin/env bash
# Copy templates/_shared into each shippable template so zips stay self-contained.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SHARED="$ROOT/templates/_shared"
TEMPLATES="$ROOT/templates"

if [[ ! -d "$SHARED" ]]; then
  echo "error: missing $SHARED" >&2
  exit 1
fi

sync_one() {
  local dir="$1"
  local id
  id="$(basename "$dir")"
  [[ "$id" == _* ]] && return 0
  [[ -f "$dir/manifest.json" ]] || return 0

  mkdir -p "$dir/bridge" "$dir/overlays"
  if [[ -f "$SHARED/bridge/orb-bridge.py" ]]; then
    cp "$SHARED/bridge/orb-bridge.py" "$dir/bridge/orb-bridge.py"
  fi
  if [[ -f "$SHARED/bridge/start-bridge.sh" ]]; then
    cp "$SHARED/bridge/start-bridge.sh" "$dir/bridge/start-bridge.sh"
    chmod +x "$dir/bridge/start-bridge.sh"
  fi
  if [[ -f "$SHARED/bridge/start-bridge.bat" ]]; then
    cp "$SHARED/bridge/start-bridge.bat" "$dir/bridge/start-bridge.bat"
  fi
  if [[ -f "$SHARED/overlays/privacy-blur.html" ]]; then
    cp "$SHARED/overlays/privacy-blur.html" "$dir/overlays/privacy-blur.html"
  fi
  echo "synced shared → $id"
}

if [[ $# -gt 0 ]]; then
  for id in "$@"; do
    sync_one "$TEMPLATES/$id"
  done
else
  shopt -s nullglob
  for dir in "$TEMPLATES"/*/; do
    sync_one "$dir"
  done
fi
