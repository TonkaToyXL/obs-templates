#!/usr/bin/env python3
"""Pure template/manifest validation helpers used by validate.sh and tests."""

from __future__ import annotations

import json
import re
from pathlib import Path

REQUIRED_MANIFEST_KEYS = ("id", "name", "version", "description")

REQUIRED_SOURCES = {
    "cozy-cabin-yeti": ("Cabin Overlay", "Yeti Voice Orb", "Stream Logo", "Mic"),
    "nebula-vibe-desk": ("Cosmic Sky", "Holographic Orb", "Stream Logo"),
}

REQUIRED_INSTALLER_FILES = (
    "install.command",
    "Install.bat",
    "install.py",
    "docs/install-guide.html",
)

BRANDING_KEYS = (
    "brandName",
    "tagLine",
    "logoFile",
    "logoOpacity",
    "accentCyan",
    "accentViolet",
    "bridgePort",
)


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def validate_manifest(folder_id: str, manifest: dict) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_MANIFEST_KEYS:
        if not manifest.get(key):
            errors.append(f"manifest missing '{key}'")
    if manifest.get("id") and manifest["id"] != folder_id:
        errors.append(
            f"manifest id '{manifest['id']}' must match folder name '{folder_id}'"
        )
    mid = manifest.get("id", "")
    if mid and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(mid)):
        errors.append("id must be kebab-case")
    version = manifest.get("version", "")
    if version and not re.fullmatch(r"\d+\.\d+\.\d+", str(version)):
        errors.append("version must be semver (e.g. 1.0.0)")
    return errors


def validate_scene_sources(folder_id: str, scene: dict) -> list[str]:
    required = REQUIRED_SOURCES.get(folder_id, ())
    if not required:
        return []
    names = {
        src.get("name")
        for src in scene.get("sources", [])
        if isinstance(src, dict) and src.get("name")
    }
    missing = [name for name in required if name not in names]
    if missing:
        return [f"scene missing sources: {', '.join(missing)}"]
    return []


def validate_port_consistency(folder: Path) -> list[str]:
    """bridgePort in branding.json must match every 127.0.0.1 port referenced by
    the scene JSON, orb.html, and README — the exact drift that once shipped a
    frozen orb. Also verifies {{INSTALL_DIR}} scene paths point at real files.
    """
    errors: list[str] = []
    folder_id = folder.name
    branding_path = folder / "branding.json"
    port: int | None = None
    if branding_path.is_file():
        try:
            port_raw = load_json(branding_path).get("bridgePort")
            port = int(port_raw) if port_raw else None
        except (OSError, json.JSONDecodeError, ValueError, TypeError):
            port = None  # invalid branding.json is reported elsewhere

    scene_dir = folder / "scene"
    for scene_path in sorted(scene_dir.glob("*.json")) if scene_dir.is_dir() else []:
        try:
            scene = load_json(scene_path)
        except (OSError, json.JSONDecodeError, ValueError):
            continue  # invalid scene JSON is reported elsewhere
        for src in scene.get("sources", []):
            if not isinstance(src, dict):
                continue
            settings = src.get("settings", {})
            if not isinstance(settings, dict):
                continue
            local_file = str(settings.get("local_file", ""))
            if "{{INSTALL_DIR}}" in local_file:
                rel = local_file.split("{{INSTALL_DIR}}/", 1)[-1].split("?", 1)[0]
                if rel and not (folder / rel).is_file():
                    errors.append(f"{folder_id}: scene references missing file: {rel}")
            if port:
                m = re.search(r"127\.0\.0\.1:(\d+)", str(settings.get("url", "")))
                if m and int(m.group(1)) != port:
                    errors.append(
                        f"{folder_id}: scene URL port {m.group(1)} != branding.json bridgePort {port}"
                    )

    if port:
        for rel in ("overlays/orb.html", "README.md"):
            path = folder / rel
            if not path.is_file():
                continue
            for m in re.finditer(
                r"127\.0\.0\.1:(\d+)", path.read_text(encoding="utf-8")
            ):
                if int(m.group(1)) != port:
                    errors.append(
                        f"{folder_id}: {rel} references port {m.group(1)} != branding.json bridgePort {port}"
                    )
    return errors


def validate_template_dir(folder: Path) -> list[str]:
    errors: list[str] = []
    folder_id = folder.name
    if folder_id.startswith("_"):
        return []

    manifest_path = folder / "manifest.json"
    if not manifest_path.is_file():
        return [f"{folder_id}: missing manifest.json"]
    if not (folder / "README.md").is_file():
        errors.append(f"{folder_id}: missing README.md")

    try:
        manifest = load_json(manifest_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"{folder_id}: invalid manifest.json ({exc})"]

    for msg in validate_manifest(folder_id, manifest):
        errors.append(f"{folder_id}: {msg}")

    for rel in REQUIRED_INSTALLER_FILES:
        if not (folder / rel).is_file():
            errors.append(f"{folder_id}: missing {rel}")

    branding_path = folder / "branding.json"
    if branding_path.is_file():
        try:
            branding = load_json(branding_path)
            for key in BRANDING_KEYS:
                if key not in branding:
                    errors.append(f"{folder_id}: branding.json missing '{key}'")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{folder_id}: invalid branding.json ({exc})")

    if manifest.get("installType") == "scene-collection":
        fonts = folder / "fonts"
        if not fonts.is_dir() or not any(fonts.glob("*.ttf")):
            errors.append(f"{folder_id}: missing fonts/*.ttf")
        previews = folder / "docs" / "previews"
        if not previews.is_dir() or not any(previews.glob("*.webp")):
            errors.append(f"{folder_id}: missing docs/previews/*.webp")
        scene_dir = folder / "scene"
        scene_files = list(scene_dir.glob("*.json")) if scene_dir.is_dir() else []
        if not scene_files:
            errors.append(f"{folder_id}: missing scene/*.json")
        else:
            try:
                scene = load_json(scene_files[0])
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                errors.append(f"{folder_id}: invalid scene JSON ({exc})")
            else:
                for msg in validate_scene_sources(folder_id, scene):
                    errors.append(f"{folder_id}: {msg}")

    errors.extend(validate_port_consistency(folder))

    return errors


def validate_templates_root(templates_root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(templates_root.iterdir()):
        if not path.is_dir() or path.name.startswith("_") or path.name.startswith("."):
            continue
        if not (path / "manifest.json").is_file():
            continue
        errors.extend(validate_template_dir(path))
    return errors


def zip_required_members(template_id: str) -> tuple[str, ...]:
    return (
        "manifest.json",
        "install.py",
        "install.command",
        "Install.bat",
        "bridge/orb-bridge.py",
        "bridge/start-bridge.sh",
        "bridge/start-bridge.bat",
        "overlays/privacy-blur.html",
        "overlays/orb.html",
        "overlays/health.html",
        "overlays/config.html",
        "branding.json",
        "assets/logo.png",
        "docs/install-guide.html",
        f"scene/{template_id}.json",
    )


if __name__ == "__main__":
    import sys

    root = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path(__file__).resolve().parents[1] / "templates"
    )
    errs = validate_templates_root(root)
    if errs:
        for err in errs:
            print(f"FAIL: {err}")
        sys.exit(1)
    print(f"  ✓ manifest_validate: {root}")
