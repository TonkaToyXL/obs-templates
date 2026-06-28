#!/usr/bin/env bash
# Start the mic-reactive overlay bridge (serves overlays + /level.json).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export OBS_BRIDGE_PORT="${OBS_BRIDGE_PORT:-8765}"
export OBS_WS_URL="${OBS_WS_URL:-ws://127.0.0.1:4455}"
if [[ -z "${OBS_MIC_INPUT:-}" && -f "$ROOT/branding.user.json" ]]; then
  export OBS_MIC_INPUT="$(python3 -c "import json;print(json.load(open('$ROOT/branding.user.json')).get('micInputName','') or '')")"
fi
if [[ -x /opt/homebrew/bin/python3 ]]; then
  PYTHON=/opt/homebrew/bin/python3
elif [[ -x /usr/local/bin/python3 ]]; then
  PYTHON=/usr/local/bin/python3
elif [[ -x /usr/bin/python3 ]]; then
  PYTHON=/usr/bin/python3
else
  PYTHON=python3
fi
# OBS WebSocket password is read from OBS's local config when needed.
exec "$PYTHON" "$ROOT/bridge/orb-bridge.py"
