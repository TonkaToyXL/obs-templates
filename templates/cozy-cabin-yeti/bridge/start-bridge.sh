#!/usr/bin/env bash
# Start the mic-reactive overlay bridge (serves overlays + /level.json).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export OBS_BRIDGE_PORT="${OBS_BRIDGE_PORT:-8766}"
export OBS_WS_URL="${OBS_WS_URL:-ws://127.0.0.1:4455}"

if [[ -x /opt/homebrew/bin/python3 ]]; then
  BASE_PYTHON=/opt/homebrew/bin/python3
elif [[ -x /usr/local/bin/python3 ]]; then
  BASE_PYTHON=/usr/local/bin/python3
elif [[ -x /usr/bin/python3 ]]; then
  BASE_PYTHON=/usr/bin/python3
else
  BASE_PYTHON=python3
fi

if [[ -z "${OBS_MIC_INPUT:-}" && -f "$ROOT/branding.user.json" ]]; then
  export OBS_MIC_INPUT="$("$BASE_PYTHON" - "$ROOT/branding.user.json" <<'PY'
import json
import sys
try:
    print(json.load(open(sys.argv[1], encoding="utf-8")).get("micInputName", "") or "")
except Exception:
    print("")
PY
)"
fi

VENV="$ROOT/bridge/.venv"
VENV_PYTHON="$VENV/bin/python"
PYTHON="$BASE_PYTHON"
if [[ -x "$VENV_PYTHON" ]]; then
  PYTHON="$VENV_PYTHON"
fi

if ! "$PYTHON" - <<'PY' >/dev/null 2>&1
import websockets
PY
then
  if [[ ! -x "$VENV_PYTHON" ]]; then
    "$BASE_PYTHON" -m venv "$VENV"
  fi
  "$VENV_PYTHON" -m pip install --upgrade websockets
  PYTHON="$VENV_PYTHON"
fi

# OBS WebSocket password is read from OBS's local config when needed.
exec "$PYTHON" "$ROOT/bridge/orb-bridge.py"
