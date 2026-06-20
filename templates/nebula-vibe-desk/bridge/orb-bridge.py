#!/usr/bin/env python3
"""Serve overlay assets and expose mic levels from OBS WebSocket."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
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
MAX_LOG_BYTES = 256_000
PORT = int(os.environ.get("OBS_BRIDGE_PORT", os.environ.get("TONKA_ORB_PORT", "8765")))
WS_URL = os.environ.get("OBS_WS_URL", os.environ.get("TONKA_OBS_WS", "ws://127.0.0.1:4455"))
WS_PASS = os.environ.get("OBS_WS_PASS", os.environ.get("TONKA_OBS_WS_PASS", ""))
INPUT_NAME = os.environ.get("OBS_MIC_INPUT", os.environ.get("TONKA_MIC_INPUT", ""))
GAIN = float(os.environ.get("OBS_ORB_GAIN", os.environ.get("TONKA_ORB_GAIN", "16.0")))

state = {
    "level": 0.0,
    "target": 0.0,
    "connected": False,
    "input_found": False,
    "meter_seen": False,
    "last_error": "",
    "status": "obs_offline",
}

_last_log_at = 0.0
_offline_logged = False


def load_branding() -> dict:
    for name in ("branding.user.json", "branding.json"):
        path = ROOT / name
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
    return {}


def mic_input_name() -> str:
    if INPUT_NAME:
        return INPUT_NAME
    return load_branding().get("micInputName", "")


def rotate_log() -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > MAX_LOG_BYTES:
            LOG_PATH.write_text(LOG_PATH.read_text(encoding="utf-8")[-MAX_LOG_BYTES:], encoding="utf-8")
    except OSError:
        pass


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
        super().end_headers()

    def do_GET(self):
        if self.path.split("?", 1)[0] == "/level.json":
            body = json.dumps(state).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


async def obs_session() -> None:
    async with websockets.connect(WS_URL, open_timeout=3) as ws:
        hello = json.loads(await ws.recv())
        auth = hello.get("d", {}).get("authentication")
        identify = {"rpcVersion": hello.get("d", {}).get("rpcVersion", 1), "eventSubscriptions": 65536}
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

        async def request(req_type: str, data: dict | None = None):
            nonlocal req_id
            req_id += 1
            await ws.send(json.dumps({"op": 6, "d": {"requestType": req_type, "requestId": f"orb-{req_id}", "requestData": data or {}}}))

        async def refresh_inputs(force: bool = False) -> None:
            nonlocal last_input_check
            now = time.time()
            if force or now - last_input_check > 8:
                last_input_check = now
                await request("GetInputList")

        await refresh_inputs(force=True)

        while True:
            msg = json.loads(await ws.recv())
            if msg.get("op") == 7 and msg.get("d", {}).get("requestType") == "GetInputList":
                inputs = msg["d"].get("responseData", {}).get("inputs", [])
                names = [i.get("inputName") for i in inputs]
                if target_mic:
                    state["input_found"] = target_mic in names
                else:
                    state["input_found"] = bool(names)
                    if names and not target_mic:
                        target_mic = names[0]
                if state["input_found"]:
                    state["status"] = "ready"
                    warned_missing = False
                elif names and target_mic:
                    state["status"] = "input_missing"
                    if not warned_missing:
                        log(f"WARNING: mic '{target_mic}' not in inputs: {names}")
                        warned_missing = True
                else:
                    state["status"] = "waiting_for_obs_inputs"
            elif msg.get("op") == 5 and msg.get("d", {}).get("eventType") == "InputVolumeMeters":
                if not state["input_found"]:
                    await refresh_inputs(force=True)
                state["meter_seen"] = True
                for inp in msg["d"].get("eventData", {}).get("inputs", []):
                    name = inp.get("inputName")
                    if target_mic and name != target_mic:
                        continue
                    if not target_mic and name:
                        target_mic = name
                    peak = peak_from_meters(inp.get("inputLevelsMul"))
                    state["target"] = state["target"] * 0.25 + peak * 0.75
                    state["level"] += (state["target"] - state["level"]) * 0.55
                    if peak > 0.02 and state["status"] != "speaking":
                        state["status"] = "speaking"
                    elif peak <= 0.02 and state["input_found"] and state["status"] == "speaking":
                        state["status"] = "ready"


async def obs_loop() -> None:
    while True:
        try:
            await obs_session()
        except Exception as exc:
            state["connected"] = False
            state["meter_seen"] = False
            state["target"] = 0.0
            state["level"] *= 0.85
            state["last_error"] = str(exc)
            state["status"] = "obs_offline"
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
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: loop.call_soon_threadsafe(loop.stop))
    loop.create_task(obs_loop())
    try:
        loop.run_forever()
    finally:
        loop.close()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log(traceback.format_exc())
        sys.exit(1)
