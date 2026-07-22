"""Canvas detection + scene scaling for responsive-canvas installs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from installer import detect_obs_canvas, scale_scene_canvas  # noqa: E402


def _scene() -> dict:
    return {
        "resolution": {"x": 2560, "y": 1440},
        "sources": [
            {
                "name": "Cosmic Sky",
                "id": "browser_source",
                "settings": {
                    "width": 2560,
                    "height": 1440,
                    "is_local_file": True,
                    "local_file": "/i/overlays/cosmic-sky.html",
                    "css": "body { width: 2560px; height: 1440px; }",
                },
            },
            {
                "name": "Brand Bar (Live)",
                "id": "browser_source",
                "settings": {
                    "width": 720,
                    "height": 90,
                    "url": "http://127.0.0.1:18765/overlays/brandbar.html?mode=live",
                },
            },
            {
                "name": "Display Capture",
                "id": "display_capture",
                "settings": {},
                "filters": [
                    {"name": "Zoom Crop", "settings": {"cx": 2560, "cy": 1440}}
                ],
            },
            {
                "name": "Vibe Coding",
                "id": "scene",
                "settings": {
                    "items": [
                        {
                            "name": "Cosmic Sky",
                            "pos": {"x": 0.0, "y": 0.0},
                            "scale_ref": {"x": 2560.0, "y": 1440.0},
                            "bounds": {"x": 2560.0, "y": 1440.0},
                        },
                        {
                            "name": "Stream Logo",
                            "pos": {"x": 48.0, "y": 48.0},
                            "scale_ref": {"x": 2560.0, "y": 1440.0},
                            "bounds": {"x": 0.0, "y": 0.0},
                        },
                        {
                            "name": "Brand Bar (Live)",
                            "pos": {"x": 0.0, "y": 1305.0},
                            "scale_ref": {"x": 2560.0, "y": 1440.0},
                            "bounds": {"x": 0.0, "y": 0.0},
                        },
                    ]
                },
            },
        ],
    }


def test_scale_to_1080p() -> None:
    out = json.loads(scale_scene_canvas(json.dumps(_scene()), 1920, 1080))
    assert out["resolution"] == {"x": 1920, "y": 1080}

    sky = out["sources"][0]
    assert sky["settings"]["width"] == 1920
    assert sky["settings"]["height"] == 1080
    assert "1920px" in sky["settings"]["css"] and "2560px" not in sky["settings"]["css"]

    # Fixed-size brand bar keeps its dimensions
    bar = out["sources"][1]
    assert bar["settings"]["width"] == 720 and bar["settings"]["height"] == 90

    # Zoom crop filter follows the canvas
    assert out["sources"][2]["filters"][0]["settings"]["cx"] == 1920
    assert out["sources"][2]["filters"][0]["settings"]["cy"] == 1080

    items = out["sources"][3]["settings"]["items"]
    assert items[0]["bounds"] == {"x": 1920.0, "y": 1080.0}
    assert items[1]["pos"] == {"x": 36.0, "y": 36.0}
    assert items[2]["pos"]["y"] == 978.75
    assert items[0]["scale_ref"] == {"x": 1920.0, "y": 1080.0}


def test_scale_noop_when_matching() -> None:
    raw = json.dumps(_scene())
    assert scale_scene_canvas(raw, 2560, 1440) == raw


def test_detect_obs_canvas_reads_profile(tmp_path: Path) -> None:
    profile = tmp_path / "basic" / "profiles" / "Main"
    profile.mkdir(parents=True)
    (profile / "basic.ini").write_text(
        "[Video]\nBaseCX=1920\nBaseCY=1080\n", encoding="utf-8"
    )
    assert detect_obs_canvas(tmp_path) == (1920, 1080)


def test_detect_obs_canvas_fallback(tmp_path: Path) -> None:
    assert detect_obs_canvas(tmp_path) == (2560, 1440)
