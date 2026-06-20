#!/usr/bin/env bash
# Start the mic-reactive overlay bridge (serves overlays + /level.json).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export OBS_BRIDGE_PORT="${OBS_BRIDGE_PORT:-8765}"
export OBS_WS_URL="${OBS_WS_URL:-ws://127.0.0.1:4455}"
# Set OBS_WS_PASS if your OBS WebSocket uses a password.
# Set OBS_MIC_INPUT to your mic name in OBS (optional — auto-detects first input).
exec python3 "$ROOT/bridge/orb-bridge.py"
