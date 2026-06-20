#!/usr/bin/env bash
# Package one or all OBS templates into dist/*.zip for direct download.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES="$ROOT/templates"
DIST="$ROOT/dist"

usage() {
  echo "Usage: $0 [template-id]"
  echo "  No args — package every template under templates/"
  echo "  Example: $0 holographic-orb"
  exit 1
}

package_one() {
  local id="$1"
  local dir="$TEMPLATES/$id"
  local manifest="$dir/manifest.json"

  if [[ ! -d "$dir" ]]; then
    echo "error: template not found: $id" >&2
    exit 1
  fi
  if [[ ! -f "$manifest" ]]; then
    echo "error: missing manifest.json in $id" >&2
    exit 1
  fi

  local version
  version="$(python3 -c "import json; print(json.load(open('$manifest'))['version'])")"
  local zip_name="${id}-v${version}.zip"
  local out="$DIST/$zip_name"

  mkdir -p "$DIST"
  rm -f "$out"

  # Zip contents at archive root (not nested in templates/id/)
  (cd "$dir" && zip -qr "$out" . -x "*.DS_Store")

  echo "created $out"
}

[[ "${1:-}" == "-h" || "${1:-}" == "--help" ]] && usage

"$ROOT/scripts/validate.sh"

mkdir -p "$DIST"

if [[ $# -eq 0 ]]; then
  shopt -s nullglob
  for dir in "$TEMPLATES"/*/; do
    base="$(basename "$dir")"
    [[ "$base" == _* ]] && continue
    package_one "$base"
  done
  "$ROOT/scripts/generate-readme-downloads.sh"
else
  package_one "$1"
  "$ROOT/scripts/generate-readme-downloads.sh"
fi
