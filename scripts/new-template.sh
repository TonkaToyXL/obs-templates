#!/usr/bin/env bash
# Scaffold a new template folder. Does not copy another template's assets.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES="$ROOT/templates"

usage() {
  echo "Usage: $0 <template-id> \"Display Name\" [overlay|scene-collection]"
  echo "  overlay           — browser sources, images (default)"
  echo "  scene-collection  — full OBS scene JSON in scene/*.json"
  exit 1
}

[[ $# -lt 2 ]] && usage

ID="$1"
NAME="$2"
INSTALL_TYPE="${3:-overlay}"

if [[ ! "$ID" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "error: id must be kebab-case (e.g. starting-soon)" >&2
  exit 1
fi

if [[ "$INSTALL_TYPE" != "overlay" && "$INSTALL_TYPE" != "scene-collection" ]]; then
  echo "error: install type must be overlay or scene-collection" >&2
  exit 1
fi

DIR="$TEMPLATES/$ID"
if [[ -d "$DIR" ]]; then
  echo "error: template already exists: $ID" >&2
  exit 1
fi

mkdir -p "$DIR/assets" "$DIR/overlays" "$DIR/docs"
[[ "$INSTALL_TYPE" == "scene-collection" ]] && mkdir -p "$DIR/scene"

cat > "$DIR/manifest.json" <<EOF
{
  "id": "$ID",
  "name": "$NAME",
  "version": "1.0.0",
  "description": "Short one-line description for the download table.",
  "obsMinVersion": "30.0",
  "installType": "$INSTALL_TYPE",
  "tags": [],
  "canvas": "any"
}
EOF

if [[ "$INSTALL_TYPE" == "scene-collection" ]]; then
  INSTALL_SECTION='## Install (easiest — double-click)

| Platform | What to double-click |
|----------|----------------------|
| **Mac** | `install.command` |
| **Windows** | `Install.bat` |

Then open OBS → **Scene Collection** → pick the **TonkaToyXL** scene.

## Scene paths

Use `{{INSTALL_DIR}}/assets/...` in your scene JSON — the installer rewrites these automatically.'
else
  INSTALL_SECTION='## Install (easiest — double-click)

| Platform | What to double-click |
|----------|----------------------|
| **Mac** | `install.command` |
| **Windows** | `Install.bat` |

Follow the browser guide that opens, or see `docs/install-guide.html`.'
fi

cat > "$DIR/README.md" <<EOF
# $NAME

Free OBS template from [TonkaToyXL](https://github.com/TonkaToyXL/obs-templates).

$INSTALL_SECTION

## Install guide (slides)

Open \`docs/install-guide.html\` — arrow keys to step through.

## Video walkthrough

_Coming soon — link will appear here after the live build stream._

## Requirements

- OBS Studio 30+

EOF

"$ROOT/scripts/generate-installers.sh" >/dev/null

echo "Created templates/$ID/ ($INSTALL_TYPE)"
echo "Next:"
echo "  1. Add files under templates/$ID/"
if [[ "$INSTALL_TYPE" == "scene-collection" ]]; then
  echo "     scene/*.json  — use {{INSTALL_DIR}} for asset paths"
fi
echo "  2. Edit manifest.json + README.md"
echo "  3. ./scripts/ship.sh \"Add $ID\""
