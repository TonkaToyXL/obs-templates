#!/usr/bin/env python3
"""Nebula Vibe Desk installer — copies assets, writes branding, registers OBS scene."""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_manifest() -> dict:
    path = ROOT / "manifest.json"
    if not path.exists():
        sys.exit("error: manifest.json not found next to installer")
    return json.loads(path.read_text(encoding="utf-8"))


def install_root(template_id: str) -> Path:
    return Path.home() / "Documents" / "OBS-Templates" / template_id


def obs_base() -> Path:
    if platform.system() == "Darwin":
        return Path.home() / "Library/Application Support/obs-studio"
    appdata = os.environ.get("APPDATA")
    if not appdata:
        sys.exit("error: APPDATA not set")
    return Path(appdata) / "obs-studio"


def obs_scenes_dir() -> Path:
    return obs_base() / "basic/scenes"


def obs_websocket_config() -> Path:
    return obs_base() / "plugin_config/obs-websocket/config.json"


def load_branding(target: Path) -> dict:
    branding = json.loads((ROOT / "branding.json").read_text(encoding="utf-8"))
    user = target / "branding.user.json"
    if user.exists():
        branding.update(json.loads(user.read_text(encoding="utf-8")))
    return branding


def write_branding_js(target: Path) -> None:
    branding = load_branding(target)
    overlays = target / "overlays"
    overlays.mkdir(parents=True, exist_ok=True)
    (overlays / "branding.js").write_text(
        "window.BRANDING = " + json.dumps(branding, indent=2) + ";\n",
        encoding="utf-8",
    )


def copy_template_files(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for name in ("assets", "overlays", "scene", "docs", "bridge", "fonts"):
        src = ROOT / name
        if src.exists() and any(src.iterdir()):
            shutil.copytree(src, target / name, dirs_exist_ok=True)
    for name in ("README.md", "manifest.json", "branding.json", "branding.user.example.json"):
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, target / name)
    write_branding_js(target)
    bridge_sh = target / "bridge" / "start-bridge.sh"
    if bridge_sh.exists():
        bridge_sh.chmod(bridge_sh.stat().st_mode | 0o111)


def patch_scene_paths(content: str, install_dir: Path) -> str:
    install = str(install_dir).replace("\\", "/")
    content = content.replace("{{INSTALL_DIR}}", install)
    for folder in ("overlays", "assets", "fonts", "bridge"):
        content = content.replace(f'"{folder}/', f'"{install}/{folder}/')
        content = content.replace(f"'{folder}/", f"'{install}/{folder}/")
    return content


def install_scene_collections(install_dir: Path, template_id: str) -> list[str]:
    scene_dir = ROOT / "scene"
    if not scene_dir.exists():
        return []

    scenes_out = obs_scenes_dir()
    scenes_out.mkdir(parents=True, exist_ok=True)
    installed: list[str] = []

    for scene_file in sorted(scene_dir.glob("*.json")):
        patched = patch_scene_paths(scene_file.read_text(encoding="utf-8"), install_dir)
        out_name = f"{template_id}.json"
        out_path = scenes_out / out_name
        out_path.write_text(patched, encoding="utf-8")
        installed.append(out_name)

    return installed


def ensure_websocket() -> tuple[bool, str]:
    cfg_path = obs_websocket_config()
    if not cfg_path.exists():
        return False, "Enable OBS WebSocket in Settings → WebSocket."

    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False, "Could not read WebSocket config."

    changed = False
    if not data.get("server_enabled"):
        data["server_enabled"] = True
        changed = True
    if not data.get("server_port"):
        data["server_port"] = 4455
        changed = True

    note = ""
    if data.get("server_password") and data.get("auth_required", True):
        note = "Set OBS_WS_PASS in bridge/start-bridge.sh if WebSocket uses a password."

    if changed:
        backup = cfg_path.with_suffix(".json.bak-template-install")
        if not backup.exists():
            shutil.copy2(cfg_path, backup)
        cfg_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    return True, note


def start_bridge(target: Path) -> None:
    script = target / "bridge" / "start-bridge.sh"
    if not script.exists() or platform.system() != "Darwin":
        return
    subprocess.Popen(
        ["/bin/bash", str(script)],
        cwd=str(target),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def open_obs() -> None:
    if platform.system() == "Darwin":
        subprocess.run(["open", "-a", "OBS"], check=False)
    elif platform.system() == "Windows":
        subprocess.run(["cmd", "/c", "start", "", "obs64.exe"], check=False)


def show_done_dialog(template_id: str, name: str) -> None:
    msg = (
        f"{name} is installed.\\n\\n"
        f"OBS → Scene Collection → {template_id}\\n"
        f"Scene → Vibe Coding. Start the bridge, then talk."
    )
    if platform.system() == "Darwin":
        subprocess.run(
            [
                "osascript",
                "-e",
                f'display dialog "{msg}" with title "Nebula Vibe Desk" buttons {{"OK"}} default button "OK"',
            ],
            check=False,
        )


def notify(title: str, message: str) -> None:
    if platform.system() == "Darwin":
        subprocess.run(
            ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
            check=False,
        )


def main() -> None:
    manifest = load_manifest()
    template_id = manifest["id"]
    install_type = manifest.get("installType", "scene-collection")
    name = manifest.get("name", template_id)

    target = install_root(template_id)
    copy_template_files(target)

    scenes: list[str] = []
    if install_type in ("scene-collection", "both"):
        scenes = install_scene_collections(target, template_id)

    ws_ok, ws_note = ensure_websocket()
    start_bridge(target)

    print()
    print(f"Installed: {name}")
    print(f"Files:     {target}")
    if scenes:
        print(f"Scene:     {obs_scenes_dir()}")
        for s in scenes:
            print(f"  • {s}")
        print()
        print(f"OBS → Scene Collection → {template_id} → Vibe Coding")
        print(f"Bridge:    {target}/bridge/start-bridge.sh")
    if ws_ok:
        print("WebSocket: local mic bridge ready (127.0.0.1)")
    if ws_note:
        print(f"Note: {ws_note}")
    print()
    print("Customize: edit branding.user.json + replace assets/logo.png")

    notify("Nebula Vibe Desk", f"{name} ready")
    if scenes:
        open_obs()
        show_done_dialog(template_id, name)
    else:
        guide = ROOT / "docs" / "install-guide.html"
        if guide.exists() and platform.system() == "Darwin":
            subprocess.run(["open", str(guide)], check=False)


if __name__ == "__main__":
    main()
