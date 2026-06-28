#!/usr/bin/env python3
"""Nebula Vibe Desk installer — copies assets, writes branding, registers OBS scene."""
from __future__ import annotations

import json
import os
import platform
import plistlib
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_manifest() -> dict:
    path = ROOT / "manifest.json"
    if not path.exists():
        sys.exit("error: manifest.json not found next to installer")
    return json.loads(path.read_text(encoding="utf-8"))


def legacy_install_root(template_id: str) -> Path:
    return Path.home() / "Documents" / "OBS-Templates" / template_id


def install_root(template_id: str) -> Path:
    if platform.system() == "Darwin":
        return Path.home() / "Library/Application Support/OBS-Templates" / template_id
    return legacy_install_root(template_id)


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


def launch_agents_dir() -> Path:
    return Path.home() / "Library/LaunchAgents"


def env_flag(name: str) -> bool:
    return os.environ.get(name, "").lower() in ("1", "true", "yes", "on")


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


def user_customizations(target: Path, legacy: Path | None = None) -> dict[str, bytes]:
    custom: dict[str, bytes] = {}
    for root in (target, legacy):
        if not root:
            continue
        for rel in ("branding.user.json", "assets/logo.png"):
            path = root / rel
            if rel not in custom and path.exists():
                custom[rel] = path.read_bytes()
    return custom


def restore_user_customizations(target: Path, custom: dict[str, bytes]) -> None:
    for rel, content in custom.items():
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def copy_template_files(target: Path, legacy: Path | None = None) -> None:
    custom = user_customizations(target, legacy)
    target.mkdir(parents=True, exist_ok=True)
    for name in ("assets", "overlays", "scene", "docs", "bridge", "fonts"):
        src = ROOT / name
        if src.exists() and any(src.iterdir()):
            shutil.copytree(src, target / name, dirs_exist_ok=True)
    for name in ("README.md", "manifest.json", "branding.json", "branding.user.example.json"):
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, target / name)
    restore_user_customizations(target, custom)
    write_branding_js(target)
    bridge_sh = target / "bridge" / "start-bridge.sh"
    if bridge_sh.exists():
        bridge_sh.chmod(bridge_sh.stat().st_mode | 0o111)
    bridge_py = target / "bridge" / "orb-bridge.py"
    if bridge_py.exists():
        bridge_py.chmod(bridge_py.stat().st_mode | 0o111)
    if platform.system() == "Darwin":
        subprocess.run(["xattr", "-cr", str(target)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def patch_scene_paths(content: str, install_dir: Path, template_id: str) -> str:
    install = str(install_dir).replace("\\", "/")
    content = content.replace("{{INSTALL_DIR}}", install)
    legacy = str(legacy_install_root(template_id)).replace("\\", "/")
    content = content.replace(legacy, install)
    for folder in ("overlays", "assets", "fonts", "bridge"):
        content = content.replace(f'"{folder}/', f'"{install}/{folder}/')
        content = content.replace(f"'{folder}/", f"'{install}/{folder}/")
    return content


def scene_collection_filename(name: str, template_id: str) -> str:
    return f"{template_id}.json"


def normalize_scene_collection(content: str, collection_name: str) -> str:
    data = json.loads(content)
    scene_names = {scene.get("name") for scene in data.get("scene_order", [])}
    data["name"] = collection_name
    if "Vibe Coding" in scene_names:
        data["current_scene"] = "Vibe Coding"
        data["current_program_scene"] = "Vibe Coding"
    for source in data.get("sources", []):
        if source.get("name") == "Holographic Orb" and source.get("id") == "browser_source":
            settings = source.setdefault("settings", {})
            settings["is_local_file"] = False
            settings["url"] = "http://127.0.0.1:8765/overlays/orb.html"
            settings.pop("local_file", None)
    return json.dumps(data, indent=4) + "\n"


def scene_collection_score(content: str) -> int:
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return -1
    names = {source.get("name") for source in data.get("sources", [])}
    if "Holographic Orb" not in names or "Vibe Coding" not in names:
        return -1
    return len(data.get("sources", []))


def current_scene_collection_file() -> str | None:
    cfg = obs_base() / "user.ini"
    if not cfg.exists():
        return None
    in_basic = False
    for line in cfg.read_text(encoding="utf-8").splitlines():
        if line.startswith("[") and line.endswith("]"):
            in_basic = line == "[Basic]"
            continue
        if in_basic and line.startswith("SceneCollectionFile="):
            return line.split("=", 1)[1].strip() or None
    return None


def best_existing_scene_collection(template_id: str, collection_name: str) -> str | None:
    scenes_out = obs_scenes_dir()
    candidates = [
        current_scene_collection_file(),
        scene_collection_filename(collection_name, template_id),
        f"{template_id}.json",
        "8.json",
    ]
    best_content: str | None = None
    best_score = -1
    seen: set[str] = set()
    for name in candidates:
        if not name or name in seen:
            continue
        seen.add(name)
        path = scenes_out / name
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        score = scene_collection_score(content)
        if score > best_score:
            best_content = content
            best_score = score
    return best_content


def install_scene_collections(install_dir: Path, template_id: str, collection_name: str) -> list[str]:
    scene_dir = ROOT / "scene"
    if not scene_dir.exists():
        return []

    scenes_out = obs_scenes_dir()
    scenes_out.mkdir(parents=True, exist_ok=True)
    installed: list[str] = []
    existing = best_existing_scene_collection(template_id, collection_name)

    for scene_file in sorted(scene_dir.glob("*.json")):
        source = existing or scene_file.read_text(encoding="utf-8")
        patched = patch_scene_paths(source, install_dir, template_id)
        patched = normalize_scene_collection(patched, collection_name)
        out_name = scene_collection_filename(collection_name, template_id)
        out_path = scenes_out / out_name
        out_path.write_text(patched, encoding="utf-8")
        installed.append(out_name)

    return installed


def set_current_scene_collection(collection_name: str, scene_file: str) -> None:
    cfg = obs_base() / "user.ini"
    if platform.system() != "Darwin" or not cfg.exists():
        return

    lines = cfg.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    in_basic = False
    saw_basic = False
    saw_collection = False
    saw_file = False

    for line in lines:
        if line.startswith("[") and line.endswith("]"):
            if in_basic:
                if not saw_collection:
                    out.append(f"SceneCollection={collection_name}")
                if not saw_file:
                    out.append(f"SceneCollectionFile={scene_file}")
            in_basic = line == "[Basic]"
            saw_basic = saw_basic or in_basic
            saw_collection = False
            saw_file = False
            out.append(line)
            continue
        if in_basic and line.startswith("SceneCollection="):
            out.append(f"SceneCollection={collection_name}")
            saw_collection = True
        elif in_basic and line.startswith("SceneCollectionFile="):
            out.append(f"SceneCollectionFile={scene_file}")
            saw_file = True
        else:
            out.append(line)

    if in_basic:
        if not saw_collection:
            out.append(f"SceneCollection={collection_name}")
        if not saw_file:
            out.append(f"SceneCollectionFile={scene_file}")
    elif not saw_basic:
        out.extend(["", "[Basic]", f"SceneCollection={collection_name}", f"SceneCollectionFile={scene_file}"])

    backup = cfg.with_suffix(".ini.bak-nebula-install")
    if not backup.exists():
        shutil.copy2(cfg, backup)
    cfg.write_text("\n".join(out) + "\n", encoding="utf-8")


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
        note = "Bridge will read the local OBS WebSocket password automatically."

    if changed:
        backup = cfg_path.with_suffix(".json.bak-template-install")
        if not backup.exists():
            shutil.copy2(cfg_path, backup)
        cfg_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    return True, note


def install_launch_agent(target: Path, branding: dict) -> tuple[bool, str]:
    script = target / "bridge" / "start-bridge.sh"
    if not script.exists() or platform.system() != "Darwin":
        return False, "LaunchAgent is only installed on macOS."

    launch_agents_dir().mkdir(parents=True, exist_ok=True)
    label = "com.nebula-vibe-desk.bridge"
    plist_path = launch_agents_dir() / f"{label}.plist"
    mic_name = str(branding.get("micInputName", "") or "")
    port = str(int(branding.get("bridgePort", 8765) or 8765))
    env = {
        "HOME": str(Path.home()),
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
        "OBS_BRIDGE_PORT": port,
    }
    if mic_name:
        env["OBS_MIC_INPUT"] = mic_name

    data = {
        "Label": label,
        "ProgramArguments": ["/bin/bash", str(script)],
        "RunAtLoad": True,
        "KeepAlive": True,
        "ThrottleInterval": 5,
        "WorkingDirectory": str(target),
        "StandardOutPath": str(target / "bridge" / "bridge.stdout.log"),
        "StandardErrorPath": str(target / "bridge" / "bridge.stderr.log"),
        "EnvironmentVariables": env,
    }
    with plist_path.open("wb") as fh:
        plistlib.dump(data, fh)
    plist_path.chmod(0o644)

    domain = f"gui/{os.getuid()}"
    subprocess.run(["launchctl", "bootout", f"{domain}/{label}"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["launchctl", "bootout", domain, str(plist_path)], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    boot = subprocess.run(["launchctl", "bootstrap", domain, str(plist_path)], check=False, capture_output=True, text=True)
    subprocess.run(["launchctl", "enable", f"{domain}/{label}"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    kick = subprocess.run(["launchctl", "kickstart", "-k", f"{domain}/{label}"], check=False, capture_output=True, text=True)
    if boot.returncode != 0:
        return False, (boot.stderr or boot.stdout or "launchctl bootstrap failed").strip()
    if kick.returncode != 0:
        return False, (kick.stderr or kick.stdout or "launchctl kickstart failed").strip()
    time.sleep(0.4)
    return True, f"{label} running from {target}"


def open_obs() -> None:
    if env_flag("OBS_TEMPLATE_NO_OPEN"):
        return
    if platform.system() == "Darwin":
        subprocess.run(["open", "-a", "OBS"], check=False)
    elif platform.system() == "Windows":
        subprocess.run(["cmd", "/c", "start", "", "obs64.exe"], check=False)


def show_done_dialog(template_id: str, name: str) -> None:
    if env_flag("OBS_TEMPLATE_SKIP_DIALOG"):
        return
    msg = (
        f"{name} is installed.\\n\\n"
        f"OBS → Scene Collection → {name}\\n"
        f"Scene → Vibe Coding\\n"
        f"Health → http://127.0.0.1:8765/health.html"
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
    if env_flag("OBS_TEMPLATE_SKIP_NOTIFY"):
        return
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
    legacy = legacy_install_root(template_id)
    copy_template_files(target, legacy if legacy != target else None)
    branding = load_branding(target)

    scenes: list[str] = []
    if install_type in ("scene-collection", "both"):
        scenes = install_scene_collections(target, template_id, name)
        if scenes:
            set_current_scene_collection(name, scenes[0])

    ws_ok, ws_note = ensure_websocket()
    bridge_ok, bridge_note = install_launch_agent(target, branding)

    print()
    print(f"Installed: {name}")
    print(f"Files:     {target}")
    if legacy.exists() and legacy != target:
        print(f"Migrated:  user branding/logo from {legacy} when present")
    if scenes:
        print(f"Scene:     {obs_scenes_dir()}")
        for s in scenes:
            print(f"  • {s}")
        print()
        print(f"OBS → Scene Collection → {name} → Vibe Coding")
        print("Orb URL:   http://127.0.0.1:8765/overlays/orb.html")
        print("Health:    http://127.0.0.1:8765/health.html")
    print(f"Bridge:    {bridge_note}")
    if ws_ok:
        print("WebSocket: local mic bridge ready (127.0.0.1)")
    if ws_note:
        print(f"Note: {ws_note}")
    if not bridge_ok:
        print("Bridge fallback: run bridge/start-bridge.sh manually if needed.")
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
