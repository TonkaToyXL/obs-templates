from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
DIST = ROOT / "dist"

import sys

sys.path.insert(0, str(ROOT / "scripts"))
from manifest_validate import (  # noqa: E402
    REQUIRED_SOURCES,
    validate_manifest,
    validate_scene_sources,
    validate_template_dir,
    validate_templates_root,
    zip_required_members,
)


def template_dirs() -> list[Path]:
    return sorted(
        p
        for p in TEMPLATES.iterdir()
        if p.is_dir() and not p.name.startswith("_") and (p / "manifest.json").is_file()
    )


def test_all_templates_validate() -> None:
    errors = validate_templates_root(TEMPLATES)
    assert errors == [], errors


@pytest.mark.parametrize("folder", template_dirs(), ids=lambda p: p.name)
def test_template_dir(folder: Path) -> None:
    errors = validate_template_dir(folder)
    assert errors == [], errors


def test_manifest_rejects_bad_id() -> None:
    errors = validate_manifest(
        "nebula-vibe-desk",
        {
            "id": "Bad_ID",
            "name": "X",
            "version": "1.0.0",
            "description": "d",
        },
    )
    assert any("kebab-case" in e for e in errors)


def test_scene_requires_stream_logo() -> None:
    scene = {"sources": [{"name": "Cosmic Sky"}, {"name": "Holographic Orb"}]}
    errors = validate_scene_sources("nebula-vibe-desk", scene)
    assert any("Stream Logo" in e for e in errors)


@pytest.mark.parametrize("folder", template_dirs(), ids=lambda p: p.name)
def test_branding_js_matches_branding_json(folder: Path) -> None:
    branding = json.loads((folder / "branding.json").read_text(encoding="utf-8"))
    js = (folder / "overlays" / "branding.js").read_text(encoding="utf-8")
    start = js.index("{")
    end = js.rindex("}") + 1
    js_branding = json.loads(js[start:end])
    for key in ("bridgePort", "logoFile", "logoOpacity", "accentCyan", "accentViolet"):
        assert js_branding.get(key) == branding.get(key), key


@pytest.mark.parametrize("folder", template_dirs(), ids=lambda p: p.name)
def test_dist_zip_contains_required_files(folder: Path) -> None:
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    zip_path = DIST / f"{folder.name}-v{manifest['version']}.zip"
    if not zip_path.exists():
        pytest.skip(f"missing {zip_path.name} — run ./scripts/package.sh")
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
    missing = [m for m in zip_required_members(folder.name) if m not in names]
    assert missing == [], missing


def test_required_sources_cover_shipped_templates() -> None:
    ids = {p.name for p in template_dirs()}
    assert set(REQUIRED_SOURCES) == ids
