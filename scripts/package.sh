#!/usr/bin/env bash
# Package one or all OBS templates into dist/*.zip for direct download.
# Keep one current, versioned zip per template.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES="$ROOT/templates"
DIST="$ROOT/dist"

usage() {
  echo "Usage: $0 [template-id]"
  echo "  No args — package every template under templates/"
  echo "  Example: $0 nebula-vibe-desk"
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
  local tmp="$DIST/.${zip_name}.tmp.zip"

  mkdir -p "$DIST"
  rm -f "$tmp"

  "$ROOT/scripts/sync-shared.sh" "$id"
  local builder="$ROOT/scripts/build-${id}-scene.py"
  if [[ -f "$builder" ]]; then
    python3 "$builder"
  elif [[ "$id" == "nebula-vibe-desk" ]]; then
    python3 "$ROOT/scripts/build-scene.py"
  fi
  "$ROOT/scripts/generate-installers.sh" >/dev/null

  # Zip contents at archive root (not nested in templates/id/)
  (cd "$dir" && zip -qr "$tmp" . \
    -x "*.DS_Store" \
    -x "__pycache__/*" \
    -x "*/__pycache__/*" \
    -x "*.pyc")

  shopt -s nullglob
  local old_zip
  for old_zip in "$DIST/${id}-v"*.zip; do
    [[ "$old_zip" == "$out" ]] && continue
    rm -f "$old_zip"
  done
  shopt -u nullglob

  mv "$tmp" "$out"

  echo "created $out"
}

[[ "${1:-}" == "-h" || "${1:-}" == "--help" ]] && usage

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

"$ROOT/scripts/validate.sh"
