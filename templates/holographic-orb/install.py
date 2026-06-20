#!/usr/bin/env python3
"""TonkaToyXL OBS template installer — copies files and registers scene collections."""
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


def obs_scenes_dir() -> Path:
    if platform.system() == "Darwin":
        return Path.home() / "Library/Application Support/obs-studio/basic/scenes"
    appdata = os.environ.get("APPDATA")
    if not appdata:
        sys.exit("error: APPDATA not set — run on Windows or set path manually")
    return Path(appdata) / "obs-studio" / "basic" / "scenes"


def copy_template_files(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for name in ("assets", "overlays", "scene", "docs"):
        src = ROOT / name
        if src.exists() and any(src.iterdir()):
            shutil.copytree(src, target / name, dirs_exist_ok=True)
    for name in ("README.md", "manifest.json"):
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, target / name)


def patch_scene_paths(content: str, install_dir: Path) -> str:
    install = str(install_dir).replace("\\", "/")
    content = content.replace("{{INSTALL_DIR}}", install)
    for folder in ("overlays", "assets"):
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
        if len(list(scene_dir.glob("*.json"))) > 1:
            out_name = f"{template_id}-{scene_file.stem}.json"
        out_path = scenes_out / out_name
        out_path.write_text(patched, encoding="utf-8")
        installed.append(out_name)

    return installed


def notify(title: str, message: str) -> None:
    if platform.system() == "Darwin":
        subprocess.run(
            ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
            check=False,
        )
    else:
        print(f"{title}: {message}")


def open_guide() -> None:
    guide = ROOT / "docs" / "install-guide.html"
    if not guide.exists():
        return
    if platform.system() == "Darwin":
        subprocess.run(["open", str(guide)], check=False)
    elif platform.system() == "Windows":
        os.startfile(guide)  # type: ignore[attr-defined]


def main() -> None:
    manifest = load_manifest()
    template_id = manifest["id"]
    install_type = manifest.get("installType", "overlay")
    name = manifest.get("name", template_id)

    target = install_root(template_id)
    copy_template_files(target)

    scenes: list[str] = []
    if install_type == "scene-collection":
        scenes = install_scene_collections(target, template_id)

    print()
    print(f"Installed: {name}")
    print(f"Files:     {target}")
    if scenes:
        print(f"Scenes:    {obs_scenes_dir()}")
        for s in scenes:
            print(f"  • {s}")
        print()
        print("Open OBS → Scene Collection → pick the new scene.")
        print("If OBS was already open, restart OBS or import from that menu.")
    else:
        print()
        print("Open docs/install-guide.html for browser-source setup steps.")

    notify("TonkaToyXL OBS", f"{name} installed")
    open_guide()


if __name__ == "__main__":
    main()
