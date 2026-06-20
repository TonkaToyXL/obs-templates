#!/usr/bin/env bash
# Scaffold a new template folder. Does not copy another template's assets.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES="$ROOT/templates"

usage() {
  echo "Usage: $0 <template-id> \"Display Name\""
  echo "  Example: $0 starting-soon \"Starting Soon Pack\""
  exit 1
}

[[ $# -lt 2 ]] && usage

ID="$1"
NAME="$2"
DIR="$TEMPLATES/$ID"

if [[ ! "$ID" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "error: id must be kebab-case (e.g. starting-soon)" >&2
  exit 1
fi

if [[ -d "$DIR" ]]; then
  echo "error: template already exists: $ID" >&2
  exit 1
fi

mkdir -p "$DIR/assets" "$DIR/overlays"

cat > "$DIR/manifest.json" <<EOF
{
  "id": "$ID",
  "name": "$NAME",
  "version": "1.0.0",
  "description": "Short one-line description for the download table.",
  "obsMinVersion": "30.0",
  "tags": [],
  "canvas": "any"
}
EOF

cat > "$DIR/README.md" <<EOF
# $NAME

Free OBS template from [TonkaToyXL](https://github.com/TonkaToyXL/obs-templates).

## Install

1. Unzip this folder anywhere permanent on your computer.
2. Add sources or import the scene collection in OBS.
3. Adjust paths if OBS asks — use **relative** files inside this folder.

## Requirements

- OBS Studio 30+

EOF

touch "$DIR/overlays/.gitkeep"
touch "$DIR/assets/.gitkeep"

echo "Created templates/$ID/"
echo "Next:"
echo "  1. Add your overlay/scene files under templates/$ID/"
echo "  2. Edit manifest.json description + README.md install steps"
echo "  3. ./scripts/validate.sh && ./scripts/package.sh $ID"
