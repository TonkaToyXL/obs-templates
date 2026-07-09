#!/usr/bin/env bash
# Start the mic-reactive overlay bridge (serves overlays + /level.json).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -x /opt/homebrew/bin/python3 ]]; then
  BASE_PYTHON=/opt/homebrew/bin/python3
elif [[ -x /usr/local/bin/python3 ]]; then
  BASE_PYTHON=/usr/local/bin/python3
elif [[ -x /usr/bin/python3 ]]; then
  BASE_PYTHON=/usr/bin/python3
else
  BASE_PYTHON=python3
fi

# Resolve bridge port + mic from branding (user overrides default).
eval "$("$BASE_PYTHON" - "$ROOT" <<'PY'
import json
import shlex
import sys
from pathlib import Path

root = Path(sys.argv[1])
branding = {}
for name in ("branding.json", "branding.user.json"):
    path = root / name
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        if isinstance(data, dict):
            branding.update(data)

port = int(branding.get("bridgePort") or 8765)
mic = str(branding.get("micInputName") or "")
print(f"RESOLVED_PORT={port}")
print(f"RESOLVED_MIC={shlex.quote(mic)}")
PY
)"

export OBS_BRIDGE_PORT="${OBS_BRIDGE_PORT:-$RESOLVED_PORT}"
export OBS_WS_URL="${OBS_WS_URL:-ws://127.0.0.1:4455}"

if [[ -z "${OBS_MIC_INPUT:-}" && -n "${RESOLVED_MIC:-}" ]]; then
  export OBS_MIC_INPUT="$RESOLVED_MIC"
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
