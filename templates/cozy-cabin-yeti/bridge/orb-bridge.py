#!/usr/bin/env python3
"""Serve overlay assets and expose mic levels from OBS WebSocket.

Canonical copy lives in templates/_shared/. Run scripts/sync-shared.sh
(or package/generate-installers) to copy into each template before ship.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import re
import signal
import sys
import threading
import time
import traceback
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    import websockets
except ImportError:
    print("Install websockets: pip3 install websockets", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT
LOG_PATH = ROOT / "bridge" / "orb-bridge.log"
LEVEL_FILE = ROOT / "overlays" / "level-live.json"
BRANDING_DEFAULT_FILE = ROOT / "branding.json"
BRANDING_USER_FILE = ROOT / "branding.user.json"
BRANDING_JS_FILE = ROOT / "overlays" / "branding.js"
MAX_LOG_BYTES = 256_000
STARTED_AT = time.time()
LOGO_SOURCE_NAME = "Stream Logo"
LOGO_FILTER_NAME = "Logo Opacity"


def _default_bridge_port() -> int:
    branding: dict = {}
    for path in (BRANDING_DEFAULT_FILE, BRANDING_USER_FILE):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            continue
        if isinstance(data, dict):
            branding.update(data)
    try:
        return int(branding.get("bridgePort", 8765) or 8765)
    except (TypeError, ValueError):
        return 8765


PORT = int(
    os.environ.get(
        "OBS_BRIDGE_PORT", os.environ.get("TONKA_ORB_PORT", str(_default_bridge_port()))
    )
)
WS_URL = os.environ.get(
    "OBS_WS_URL", os.environ.get("TONKA_OBS_WS", "ws://127.0.0.1:4455")
)
WS_PASS = os.environ.get("OBS_WS_PASS", os.environ.get("TONKA_OBS_WS_PASS", ""))


def _obs_ws_password_from_config() -> str:
    """Read OBS's local WebSocket password without logging or storing it."""
    candidates = [
        Path.home()
        / "Library"
        / "Application Support"
        / "obs-studio"
        / "plugin_config"
        / "obs-websocket"
        / "config.json",
        Path.home() / ".config/obs-studio/plugin_config/obs-websocket/config.json",
        Path(os.environ.get("APPDATA", ""))
        / "obs-studio/plugin_config/obs-websocket/config.json",
    ]
    for path in candidates:
        try:
            if path.is_file():
                cfg = json.loads(path.read_text(encoding="utf-8"))
                if cfg.get("auth_required") and cfg.get("server_password"):
                    return str(cfg["server_password"])
        except (OSError, json.JSONDecodeError, ValueError):
            continue
    return ""


if not WS_PASS:
    WS_PASS = _obs_ws_password_from_config()
INPUT_NAME = os.environ.get("OBS_MIC_INPUT", os.environ.get("TONKA_MIC_INPUT", ""))
GAIN = float(os.environ.get("OBS_ORB_GAIN", os.environ.get("TONKA_ORB_GAIN", "32.0")))

# Auto-pick heuristics, used only when no mic is configured. Skip obvious
# non-mic sources; prefer names that look like microphones. Keep these generic
# — never put your specific device names here.
SKIP_MIC_SUBSTR = (
    "display",
    "desktop",
    "monitor",
    "streambeats",
    "yt alert",
    "yt like",
    "like counter",
    "replay",
    "output",
)
PREFER_MIC_SUBSTR = (
    "headset",
    "external microphone",
    "external mic",
    "mic/aux",
    " microphone",
)
ORB_POSITIONS = ("lowerRight", "rightEdge", "centerRight", "lowerCenter")
CONFIG_SCHEMA = {
    "brandName": {"type": "text", "maxLength": 48},
    "tagLine": {"type": "text", "maxLength": 72},
    "logoFile": {"type": "path", "maxLength": 160},
    "logoOpacity": {"type": "number", "min": 0, "max": 1},
    "accentCyan": {"type": "color"},
    "accentViolet": {"type": "color"},
    "micInputName": {"type": "text", "maxLength": 120},
    "orbPosition": {"type": "select", "options": ORB_POSITIONS},
    "orbScale": {"type": "number", "min": 0.72, "max": 1.4},
    "voiceSensitivity": {"type": "number", "min": 0.45, "max": 2.4},
    "glowIntensity": {"type": "number", "min": 0.45, "max": 1.8},
}

state = {
    "level": 0.0,
    "target": 0.0,
    "peak_db": -100.0,
    "input_name": "",
    "connected": False,
    "input_found": False,
    "meter_seen": False,
    "last_error": "",
    "port": PORT,
    "status": "obs_offline",
    "logo_apply_status": "idle",
    "logo_apply_error": "",
}

_pending_logo: dict | None = None
_pending_logo_lock = threading.Lock()
_last_log_at = 0.0
_offline_logged = False


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def load_branding() -> dict:
    branding = read_json(BRANDING_DEFAULT_FILE)
    branding.update(read_json(BRANDING_USER_FILE))
    return branding


def write_branding_js(branding: dict) -> None:
    BRANDING_JS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = BRANDING_JS_FILE.with_suffix(".js.tmp")
    tmp.write_text(
        "window.BRANDING = " + json.dumps(branding, indent=2) + ";\n",
        encoding="utf-8",
    )
    tmp.replace(BRANDING_JS_FILE)


def clamp_number(value, lo: float, hi: float) -> float:
    try:
        num = float(value)
    except (TypeError, ValueError):
        raise ValueError("not a number") from None
    if num < lo:
        return lo
    if num > hi:
        return hi
    return round(num, 3)


def clean_text(value, max_length: int) -> str:
    text = str(value or "").replace("\x00", "").strip()
    return text[:max_length]


def clean_relative_path(value, max_length: int) -> str:
    text = clean_text(value, max_length).replace("\\", "/")
    if not text or text.startswith("/") or ".." in Path(text).parts:
        raise ValueError("path must be relative to the template")
    return text


def clean_color(value) -> str:
    text = clean_text(value, 16)
    if re.fullmatch(r"#[0-9a-fA-F]{3}", text):
        return "#" + "".join(ch * 2 for ch in text[1:]).lower()
    if re.fullmatch(r"#[0-9a-fA-F]{6}", text):
        return text.lower()
    raise ValueError("color must be #RGB or #RRGGBB")


def sanitize_config(payload: dict) -> tuple[dict, dict]:
    if not isinstance(payload, dict):
        raise ValueError("config payload must be a JSON object")
    incoming = (
        payload.get("config") if isinstance(payload.get("config"), dict) else payload
    )
    clean: dict = {}
    errors: dict = {}
    for key, spec in CONFIG_SCHEMA.items():
        if key not in incoming:
            continue
        try:
            if spec["type"] == "number":
                clean[key] = clamp_number(incoming[key], spec["min"], spec["max"])
            elif spec["type"] == "color":
                clean[key] = clean_color(incoming[key])
            elif spec["type"] == "select":
                value = str(incoming[key])
                if value not in spec["options"]:
                    raise ValueError("unknown option")
                clean[key] = value
            elif spec["type"] == "path":
                clean[key] = clean_relative_path(incoming[key], spec["maxLength"])
            else:
                clean[key] = clean_text(incoming[key], spec["maxLength"])
        except ValueError as exc:
            errors[key] = str(exc)
    return clean, errors


def config_payload() -> dict:
    return {
        "config": load_branding(),
        "schema": CONFIG_SCHEMA,
        "runtime": {
            "root": str(ROOT),
            "config_file": str(BRANDING_USER_FILE),
            "branding_js": str(BRANDING_JS_FILE),
        },
    }


def mic_input_name() -> str:
    if INPUT_NAME:
        return INPUT_NAME
    return load_branding().get("micInputName", "")


def pick_mic_input(names: list[str], preferred: str) -> str:
    if preferred and preferred in names:
        return preferred
    clean = [n for n in names if n and not any(s in n.lower() for s in SKIP_MIC_SUBSTR)]
    for hint in PREFER_MIC_SUBSTR:
        for name in clean:
            if hint in name.lower():
                return name
    return clean[0] if clean else (names[0] if names else "")


def rotate_log() -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > MAX_LOG_BYTES:
            LOG_PATH.write_text(
                LOG_PATH.read_text(encoding="utf-8")[-MAX_LOG_BYTES:], encoding="utf-8"
            )
    except OSError:
        pass


def write_level_file() -> None:
    try:
        LEVEL_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = LEVEL_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(state), encoding="utf-8")
        tmp.replace(LEVEL_FILE)
    except OSError:
        pass


def health_payload() -> dict:
    return {
        "bridge_status": "running",
        "uptime_seconds": round(time.time() - STARTED_AT, 1),
        "port": PORT,
        "root": str(ROOT),
        "obs_connected": state["connected"],
        "mic_input_name": state["input_name"],
        "mic_found": state["input_found"],
        "meter_seen": state["meter_seen"],
        "level": state["level"],
        "target": state["target"],
        "peak_db": state["peak_db"],
        "status": state["status"],
        "last_error": state["last_error"],
        "logo_apply_status": state["logo_apply_status"],
        "logo_apply_error": state["logo_apply_error"],
    }


def log(msg: str, *, throttle_offline: bool = False) -> None:
    global _last_log_at, _offline_logged
    now = time.time()
    if throttle_offline:
        if _offline_logged and now - _last_log_at < 60:
            return
        _offline_logged = True
    else:
        _offline_logged = False
    _last_log_at = now
    rotate_log()
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n"
    try:
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError:
        pass


def sha256_b64(text: str) -> str:
    return base64.b64encode(hashlib.sha256(text.encode()).digest()).decode()


def peak_from_meters(levels_mul) -> float:
    peak = 0.0
    if not levels_mul:
        return 0.0
    for ch in levels_mul:
        if not ch:
            continue
        for v in ch:
            if v > peak:
                peak = v
    scaled = peak * GAIN
    return min(1.0, 1.0 - pow(2.718281828, -scaled * 4.5))


def peak_from_input(inp: dict) -> tuple[float, float]:
    peak_db = -100.0
    for ch in inp.get("inputLevelsDb") or []:
        if not ch:
            continue
        for value in ch:
            if value > peak_db:
                peak_db = value
    if peak_db > -95.0:
        normalized = (peak_db + 55.0) / 43.0
        return min(1.0, max(0.0, normalized)), peak_db
    return peak_from_meters(inp.get("inputLevelsMul")), peak_db


def queue_logo_apply(branding: dict) -> None:
    global _pending_logo
    payload = {
        "logoFile": branding.get("logoFile", "assets/logo.png"),
        "logoOpacity": branding.get("logoOpacity", 0.52),
    }
    with _pending_logo_lock:
        _pending_logo = payload
    state["logo_apply_status"] = "queued"
    state["logo_apply_error"] = ""


def take_pending_logo() -> dict | None:
    global _pending_logo
    with _pending_logo_lock:
        payload = _pending_logo
        _pending_logo = None
        return payload


def resolve_logo_path(rel: str) -> Path:
    path = (ROOT / clean_relative_path(rel, 160)).resolve()
    if not str(path).startswith(str(ROOT.resolve())):
        raise ValueError("logo path escapes template root")
    return path


class BridgeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ASSETS), **kwargs)

    def log_message(self, fmt, *args):
        return

    def end_headers(self):
        path = self.path.split("?", 1)[0]
        if path.endswith((".html", ".json", ".js")):
            self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS, POST")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def local_origin_allowed(self) -> bool:
        origin = self.headers.get("Origin", "")
        return (
            not origin
            or origin.startswith(f"http://127.0.0.1:{PORT}")
            or origin.startswith(f"http://localhost:{PORT}")
        )

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/level.json":
            self.send_json(state)
            return
        if path == "/health.json":
            self.send_json(health_payload())
            return
        if path == "/config.json":
            self.send_json(config_payload())
            return
        if path == "/health.html":
            self.path = "/overlays/health.html"
        elif path == "/config.html":
            self.path = "/overlays/config.html"
        super().do_GET()

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path != "/config.json":
            self.send_error(404)
            return
        if not self.local_origin_allowed():
            self.send_json(
                {
                    "ok": False,
                    "error": "config writes must come from the local bridge page",
                },
                403,
            )
            return
        try:
            length = int(self.headers.get("Content-Length", "0") or 0)
        except ValueError:
            self.send_json({"ok": False, "error": "invalid content length"}, 400)
            return
        if length < 1 or length > 32768:
            self.send_json(
                {"ok": False, "error": "config payload is empty or too large"}, 413
            )
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            clean, errors = sanitize_config(payload)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            self.send_json({"ok": False, "error": str(exc)}, 400)
            return
        if errors:
            self.send_json({"ok": False, "errors": errors, **config_payload()}, 422)
            return
        try:
            existing = read_json(BRANDING_USER_FILE)
            existing.update(clean)
            BRANDING_USER_FILE.parent.mkdir(parents=True, exist_ok=True)
            tmp = BRANDING_USER_FILE.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
            tmp.replace(BRANDING_USER_FILE)
            branding = load_branding()
            write_branding_js(branding)
        except OSError as exc:
            self.send_json({"ok": False, "error": str(exc)}, 500)
            return
        if "logoFile" in clean or "logoOpacity" in clean:
            queue_logo_apply(branding)
        self.send_json({"ok": True, **config_payload()})

    def do_HEAD(self):
        path = self.path.split("?", 1)[0]
        if path == "/health.html":
            self.path = "/overlays/health.html"
        elif path == "/config.html":
            self.path = "/overlays/config.html"
        super().do_HEAD()


async def apply_logo_to_obs(request, branding_slice: dict) -> None:
    """Push logo path/opacity into OBS. Soft-fails if source missing or OBS rejects."""
    state["logo_apply_status"] = "applying"
    state["logo_apply_error"] = ""
    try:
        logo_rel = str(branding_slice.get("logoFile") or "assets/logo.png")
        opacity = float(branding_slice.get("logoOpacity", 0.52))
        logo_path = resolve_logo_path(logo_rel)
        if not logo_path.is_file():
            raise FileNotFoundError(f"logo file not found: {logo_rel}")
        await request(
            "SetInputSettings",
            {
                "inputName": LOGO_SOURCE_NAME,
                "inputSettings": {"file": str(logo_path)},
                "overlay": True,
            },
        )
        await request(
            "SetSourceFilterSettings",
            {
                "sourceName": LOGO_SOURCE_NAME,
                "filterName": LOGO_FILTER_NAME,
                "filterSettings": {"opacity": opacity},
            },
        )
        state["logo_apply_status"] = "applied"
        log(f"Applied logo to OBS: {logo_rel} opacity={opacity}")
    except Exception as exc:
        state["logo_apply_status"] = "failed"
        state["logo_apply_error"] = str(exc)
        log(f"Logo apply soft-fail (config still saved): {exc}")


async def obs_session() -> None:
    async with websockets.connect(WS_URL, open_timeout=3) as ws:
        hello = json.loads(await ws.recv())
        auth = hello.get("d", {}).get("authentication")
        identify = {
            "rpcVersion": hello.get("d", {}).get("rpcVersion", 1),
            "eventSubscriptions": 65536,
        }
        if auth and WS_PASS:
            secret = sha256_b64(WS_PASS + auth["salt"])
            identify["authentication"] = sha256_b64(secret + auth["challenge"])
        await ws.send(json.dumps({"op": 1, "d": identify}))
        identified = json.loads(await ws.recv())
        if identified.get("op") != 2:
            raise RuntimeError(f"obs identify failed: {identified}")

        state["connected"] = True
        state["last_error"] = ""
        state["status"] = "connected"
        log("Connected to OBS WebSocket")

        req_id = 0
        last_input_check = 0.0
        warned_missing = False
        target_mic = mic_input_name()
        state["input_name"] = target_mic

        async def request(req_type: str, data: dict | None = None):
            nonlocal req_id
            req_id += 1
            await ws.send(
                json.dumps(
                    {
                        "op": 6,
                        "d": {
                            "requestType": req_type,
                            "requestId": f"orb-{req_id}",
                            "requestData": data or {},
                        },
                    }
                )
            )

        async def refresh_inputs(force: bool = False) -> None:
            nonlocal last_input_check, target_mic, warned_missing
            now = time.time()
            if force or now - last_input_check > 8:
                last_input_check = now
                preferred = mic_input_name()
                if not INPUT_NAME and preferred and preferred != target_mic:
                    target_mic = preferred
                    state["input_name"] = target_mic
                    warned_missing = False
                await request("GetInputList")

        await refresh_inputs(force=True)
        pending = take_pending_logo()
        if pending:
            await apply_logo_to_obs(request, pending)

        while True:
            pending = take_pending_logo()
            if pending:
                await apply_logo_to_obs(request, pending)

            try:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=0.35))
            except asyncio.TimeoutError:
                continue

            if (
                msg.get("op") == 7
                and msg.get("d", {}).get("requestType") == "GetInputList"
            ):
                inputs = msg["d"].get("responseData", {}).get("inputs", [])
                names = [i.get("inputName") for i in inputs if i.get("inputName")]
                if not INPUT_NAME and not load_branding().get("micInputName"):
                    picked = pick_mic_input(names, target_mic)
                    if picked and picked != target_mic:
                        target_mic = picked
                if target_mic:
                    state["input_found"] = target_mic in names
                else:
                    state["input_found"] = bool(names)
                    if names:
                        target_mic = pick_mic_input(names, "")
                if state["input_found"]:
                    state["status"] = "ready"
                    state["input_name"] = target_mic
                    warned_missing = False
                elif names and target_mic:
                    state["status"] = "input_missing"
                    if not warned_missing:
                        log(f"WARNING: mic '{target_mic}' not in inputs: {names}")
                        warned_missing = True
                else:
                    state["status"] = "waiting_for_obs_inputs"
            elif (
                msg.get("op") == 5
                and msg.get("d", {}).get("eventType") == "InputVolumeMeters"
            ):
                if not state["input_found"]:
                    await refresh_inputs(force=True)
                state["meter_seen"] = True
                for inp in msg["d"].get("eventData", {}).get("inputs", []):
                    name = inp.get("inputName")
                    if target_mic and name != target_mic:
                        continue
                    if not target_mic and name:
                        target_mic = name
                    peak, peak_db = peak_from_input(inp)
                    state["peak_db"] = peak_db
                    state["target"] = state["target"] * 0.25 + peak * 0.75
                    state["level"] += (state["target"] - state["level"]) * 0.55
                    if peak > 0.04 and state["status"] != "speaking":
                        state["status"] = "speaking"
                    elif (
                        peak <= 0.04
                        and state["input_found"]
                        and state["status"] == "speaking"
                    ):
                        state["status"] = "ready"
                    write_level_file()


async def obs_loop() -> None:
    while True:
        try:
            await obs_session()
        except Exception as exc:
            state["connected"] = False
            state["meter_seen"] = False
            state["input_found"] = False
            state["target"] = 0.0
            state["level"] *= 0.85
            state["last_error"] = str(exc)
            state["status"] = "obs_offline"
            if state["logo_apply_status"] == "queued":
                state["logo_apply_status"] = "pending_obs"
                state["logo_apply_error"] = (
                    "OBS offline — logo will apply when OBS reconnects"
                )
            write_level_file()
            log(f"OBS WebSocket offline: {exc}", throttle_offline=True)
            await asyncio.sleep(3)


def run_http() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", PORT), BridgeHandler)
    log(f"Overlay bridge listening on http://127.0.0.1:{PORT}/")
    server.serve_forever()


def main() -> None:
    os.chdir(ASSETS)
    threading.Thread(target=run_http, daemon=True).start()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def stop_loop(*_args) -> None:
        if not loop.is_closed():
            loop.call_soon_threadsafe(loop.stop)

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, stop_loop)
    task = loop.create_task(obs_loop())
    try:
        loop.run_forever()
    finally:
        task.cancel()
        loop.run_until_complete(asyncio.gather(task, return_exceptions=True))
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log(traceback.format_exc())
        sys.exit(1)
