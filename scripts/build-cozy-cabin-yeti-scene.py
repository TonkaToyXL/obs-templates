#!/usr/bin/env python3
"""Generate OBS scene collection for Cozy Cabin Yeti."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
TEMPLATE = REPO_ROOT / "templates" / "cozy-cabin-yeti"
OUT = TEMPLATE / "scene" / "cozy-cabin-yeti.json"
BRANDING_PATH = TEMPLATE / "branding.json"
BRANDING = json.loads(BRANDING_PATH.read_text(encoding="utf-8")) if BRANDING_PATH.exists() else {}
BRIDGE_PORT = int(BRANDING.get("bridgePort", 8766) or 8766)

W, H = 2560, 1440
INSTALL = "{{INSTALL_DIR}}"
ORIGIN = f"http://127.0.0.1:{BRIDGE_PORT}"
MAIN_CANVAS_UUID = "6c69626f-6273-4c00-9d88-c5136d61696e"
ZOOM_FILTER_NAME = "obs-zoom-to-mouse-crop"


def uid(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"obs-template:cozy-cabin-yeti:{name}"))


ids = {
    key: uid(key)
    for key in (
        "display",
        "cabin",
        "orb",
        "brand-live",
        "brand-soon",
        "privacy",
        "soon",
        "mic",
        "scene-vibe",
        "scene-soon",
    )
}


def base_source(name: str, source_id: str, source_uuid: str, settings: dict) -> dict:
    return {
        "prev_ver": 503382018,
        "name": name,
        "uuid": source_uuid,
        "id": source_id,
        "versioned_id": source_id,
        "settings": settings,
        "mixers": 0,
        "sync": 0,
        "flags": 0,
        "volume": 1.0,
        "balance": 0.5,
        "enabled": True,
        "muted": False,
        "push-to-mute": False,
        "push-to-mute-delay": 0,
        "push-to-talk": False,
        "push-to-talk-delay": 0,
        "hotkeys": {},
        "deinterlace_mode": 0,
        "deinterlace_field_order": 0,
        "monitoring_type": 0,
        "filters": [],
        "private_settings": {},
    }


def zoom_crop_filter() -> dict:
    return {
        "prev_ver": 536936450,
        "name": ZOOM_FILTER_NAME,
        "uuid": uid(ZOOM_FILTER_NAME),
        "id": "crop_filter",
        "versioned_id": "crop_filter",
        "settings": {"left": 0, "top": 0, "cx": W, "cy": H, "relative": False},
        "mixers": 0,
        "sync": 0,
        "flags": 0,
        "volume": 1.0,
        "balance": 0.5,
        "enabled": True,
        "muted": False,
        "push-to-mute": False,
        "push-to-mute-delay": 0,
        "push-to-talk": False,
        "push-to-talk-delay": 0,
        "hotkeys": {},
        "deinterlace_mode": 0,
        "deinterlace_field_order": 0,
        "monitoring_type": 0,
        "private_settings": {},
    }


def browser(name: str, source_uuid: str, rel_path: str, w: int, h: int, *, local: bool = True) -> dict:
    settings = {
        "width": w,
        "height": h,
        "fps": 30,
        "shutdown": False,
        "restart_when_active": True,
        "css": "",
        "reroute_audio": False,
    }
    if local:
        settings["is_local_file"] = True
        settings["local_file"] = f"{INSTALL}/{rel_path}"
    else:
        settings["is_local_file"] = False
        settings["url"] = rel_path
    return base_source(name, "browser_source", source_uuid, settings)


def audio_input(name: str, source_uuid: str) -> dict:
    source = base_source(
        name,
        "coreaudio_input_capture",
        source_uuid,
        {"device_id": "default"},
    )
    source["mixers"] = 255
    source["hotkeys"] = {
        "libobs.mute": [],
        "libobs.unmute": [],
        "libobs.push-to-mute": [],
        "libobs.push-to-talk": [],
    }
    return source


def scene_item(
    name: str,
    source_uuid: str,
    item_id: int,
    pos: tuple[float, float] = (0, 0),
    scale: tuple[float, float] = (1, 1),
    bounds: tuple[float, float] | None = None,
    bounds_type: int = 0,
    visible: bool = True,
) -> dict:
    return {
        "name": name,
        "source_uuid": source_uuid,
        "visible": visible,
        "locked": False,
        "rot": 0.0,
        "scale_ref": {"x": float(W), "y": float(H)},
        "align": 5,
        "bounds_type": bounds_type,
        "bounds_align": 0,
        "bounds_crop": False,
        "crop_left": 0,
        "crop_top": 0,
        "crop_right": 0,
        "crop_bottom": 0,
        "id": item_id,
        "group_item_backup": False,
        "pos": {"x": float(pos[0]), "y": float(pos[1])},
        "pos_rel": {"x": 0.0, "y": 0.0},
        "scale": {"x": float(scale[0]), "y": float(scale[1])},
        "scale_rel": {"x": float(scale[0]), "y": float(scale[1])},
        "bounds": {"x": float(bounds[0]) if bounds else 0.0, "y": float(bounds[1]) if bounds else 0.0},
        "bounds_rel": {"x": float(bounds[0]) if bounds else 0.0, "y": float(bounds[1]) if bounds else 0.0},
        "scale_filter": "disable",
        "blend_method": "default",
        "blend_type": "normal",
        "show_transition": {"duration": 0},
        "hide_transition": {"duration": 0},
        "private_settings": {},
    }


def make_scene(name: str, source_uuid: str, items: list[dict]) -> dict:
    scene = base_source(name, "scene", source_uuid, {})
    scene["settings"] = {"items": items, "custom_size": False, "id_counter": len(items) + 1}
    scene["canvas_uuid"] = MAIN_CANVAS_UUID
    return scene


display = base_source(
    "Display Capture",
    "screen_capture",
    ids["display"],
    {
        "capture_cursor": True,
        "show_cursor": True,
        "capture_mode": "display",
        "type": "display_capture",
    },
)
display["filters"] = [zoom_crop_filter()]

vibe_items = [
    scene_item("Display Capture", ids["display"], 1, bounds=(W, H), bounds_type=2),
    scene_item("Cabin Overlay", ids["cabin"], 2, bounds=(W, H), bounds_type=2),
    scene_item("Privacy Mask", ids["privacy"], 3, visible=False),
    scene_item("Cabin Brand Bar", ids["brand-live"], 4, pos=(38, 1304), scale=(0.926, 0.926)),
    scene_item("Yeti Voice Orb", ids["orb"], 5),
    scene_item("Mic", ids["mic"], 6),
]

soon_items = [
    scene_item("Display Capture", ids["display"], 1, bounds=(W, H), bounds_type=2),
    scene_item("Cabin Starting Soon", ids["soon"], 2, bounds=(W, H), bounds_type=2),
    scene_item("Yeti Voice Orb", ids["orb"], 3),
    scene_item("Cabin Brand Bar (Soon)", ids["brand-soon"], 4, pos=(38, 1304), scale=(0.926, 0.926)),
    scene_item("Mic", ids["mic"], 5),
]

collection = {
    "current_scene": "Vibe Coding",
    "current_program_scene": "Vibe Coding",
    "scene_order": [{"name": "Starting Soon"}, {"name": "Vibe Coding"}],
    "name": "Cozy Cabin Yeti",
    "sources": [
        display,
        browser("Cabin Overlay", ids["cabin"], "overlays/cabin.html", W, H),
        browser("Privacy Mask", ids["privacy"], "overlays/privacy-blur.html", W, H),
        browser("Cabin Brand Bar", ids["brand-live"], f"{ORIGIN}/overlays/brandbar.html?mode=live", 720, 90, local=False),
        browser("Yeti Voice Orb", ids["orb"], f"{ORIGIN}/overlays/orb.html", W, H, local=False),
        browser("Cabin Starting Soon", ids["soon"], "overlays/soon-backdrop.html", W, H),
        browser("Cabin Brand Bar (Soon)", ids["brand-soon"], f"{ORIGIN}/overlays/brandbar.html?mode=soon", 720, 90, local=False),
        audio_input("Mic", ids["mic"]),
        make_scene("Vibe Coding", ids["scene-vibe"], vibe_items),
        make_scene("Starting Soon", ids["scene-soon"], soon_items),
    ],
    "groups": [],
    "quick_transitions": [
        {"name": "Cut", "duration": 300, "hotkeys": [], "id": 3, "fade_to_black": False},
        {"name": "Fade", "duration": 600, "hotkeys": [], "id": 4, "fade_to_black": False},
        {"name": "Fade", "duration": 600, "hotkeys": [], "id": 5, "fade_to_black": True},
    ],
    "transitions": [],
    "saved_projectors": [],
    "canvases": [],
    "current_transition": "Fade",
    "transition_duration": 300,
    "resolution": {"x": W, "y": H},
    "preview_locked": False,
    "scaling_enabled": False,
    "scaling_level": -15,
    "scaling_off_x": 0.0,
    "scaling_off_y": 0.0,
    "version": 2,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(collection, indent=4) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
