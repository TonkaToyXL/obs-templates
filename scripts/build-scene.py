#!/usr/bin/env python3
"""Generate OBS scene collection for Nebula Vibe Desk template."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
if (REPO_ROOT / "templates" / "nebula-vibe-desk").is_dir():
    TEMPLATE = REPO_ROOT / "templates" / "nebula-vibe-desk"
else:
    TEMPLATE = REPO_ROOT
OUT = TEMPLATE / "scene" / "nebula-vibe-desk.json"
BRANDING_PATH = TEMPLATE / "branding.json"
BRANDING = json.loads(BRANDING_PATH.read_text()) if BRANDING_PATH.exists() else {}
BRIDGE_PORT = int(BRANDING.get("bridgePort", 8765) or 8765)

W, H = 2560, 1440
INSTALL = "{{INSTALL_DIR}}"
MAIN_CANVAS_UUID = "6c69626f-6273-4c00-9d88-c5136d61696e"
ZOOM_FILTER_NAME = "obs-zoom-to-mouse-crop"

# Stable uuids keep generated scene files reviewable between package runs.
def uid(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"tonkatoyxl:obs-template:nebula-vibe-desk:{name}"))


ids = {k: uid(k) for k in (
    "cosmic", "orb", "logo", "brand_live", "brand_soon", "privacy", "soon_bg",
    "scene_vibe", "scene_soon",
)}

COSMIC_CSS = (
    "body { background-color: rgba(0,0,0,0); margin: 0px auto; "
    "overflow: hidden; width: 2560px; height: 1440px; }"
)


def browser(name, u, rel_path, w, h, css="", local=True):
    settings = {
        "width": w,
        "height": h,
        "fps": 30,
        "shutdown": False,
        "restart_when_active": True,
        "css": css,
        "reroute_audio": False,
    }
    if local:
        settings["is_local_file"] = True
        settings["local_file"] = f"{INSTALL}/{rel_path}"
    else:
        settings["is_local_file"] = False
        settings["url"] = rel_path
    return {
        "prev_ver": 503382018,
        "name": name,
        "uuid": u,
        "id": "browser_source",
        "versioned_id": "browser_source",
        "settings": settings,
        "mixers": 0, "sync": 0, "flags": 0, "volume": 1.0, "balance": 0.5,
        "enabled": True, "muted": False,
        "push-to-mute": False, "push-to-mute-delay": 0,
        "push-to-talk": False, "push-to-talk-delay": 0,
        "hotkeys": {},
        "deinterlace_mode": 0, "deinterlace_field_order": 0, "monitoring_type": 0,
        "filters": [],
        "private_settings": {},
    }


def image_logo(name, u, opacity):
    return {
        "prev_ver": 503382018,
        "name": name,
        "uuid": u,
        "id": "image_source",
        "versioned_id": "image_source",
        "settings": {
            "file": f"{INSTALL}/assets/logo.png",
            "unload": False,
        },
        "mixers": 0, "sync": 0, "flags": 0, "volume": 1.0, "balance": 0.5,
        "enabled": True, "muted": False,
        "push-to-mute": False, "push-to-mute-delay": 0,
        "push-to-talk": False, "push-to-talk-delay": 0,
        "hotkeys": {},
        "deinterlace_mode": 0, "deinterlace_field_order": 0, "monitoring_type": 0,
        "private_settings": {},
        "filters": [
            {
                "prev_ver": 503382018,
                "name": "Logo Opacity",
                "uuid": uid(f"{name}:logo-opacity"),
                "id": "mask_filter",
                "versioned_id": "mask_filter",
                "settings": {"opacity": opacity},
                "mixers": 0, "sync": 0, "flags": 0, "volume": 1.0, "balance": 0.5,
                "enabled": True, "muted": False,
                "push-to-mute": False, "push-to-mute-delay": 0,
                "push-to-talk": False, "push-to-talk-delay": 0,
                "hotkeys": {},
                "deinterlace_mode": 0, "deinterlace_field_order": 0, "monitoring_type": 0,
                "private_settings": {},
            }
        ],
    }


def zoom_crop_filter():
    return {
        "prev_ver": 536936450,
        "name": ZOOM_FILTER_NAME,
        "uuid": uid(ZOOM_FILTER_NAME),
        "id": "crop_filter",
        "versioned_id": "crop_filter",
        "settings": {"left": 0, "top": 0, "cx": W, "cy": H, "relative": False},
        "mixers": 0, "sync": 0, "flags": 0, "volume": 1.0, "balance": 0.5,
        "enabled": True, "muted": False,
        "push-to-mute": False, "push-to-mute-delay": 0,
        "push-to-talk": False, "push-to-talk-delay": 0,
        "hotkeys": {},
        "deinterlace_mode": 0, "deinterlace_field_order": 0, "monitoring_type": 0,
        "private_settings": {},
    }


def scene_item(name, source_uuid, item_id, pos=(0, 0), scale=(1, 1), bounds=None, bounds_type=0, visible=True):
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
        "crop_left": 0, "crop_top": 0, "crop_right": 0, "crop_bottom": 0,
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


def make_scene(name, u, canvas_u, items):
    return {
        "prev_ver": 503382018,
        "name": name,
        "uuid": u,
        "id": "scene",
        "versioned_id": "scene",
        "settings": {
            "items": items,
            "custom_size": False,
            "id_counter": len(items) + 1,
        },
        "mixers": 0, "sync": 0, "flags": 0, "volume": 1.0, "balance": 0.5,
        "enabled": True, "muted": False,
        "push-to-mute": False, "push-to-mute-delay": 0,
        "push-to-talk": False, "push-to-talk-delay": 0,
        "hotkeys": {},
        "deinterlace_mode": 0, "deinterlace_field_order": 0, "monitoring_type": 0,
        "filters": [],
        "canvas_uuid": canvas_u,
        "private_settings": {},
    }


display_id = uid("display")

vibe_items = [
    scene_item("Display Capture", display_id, 1, (0, 0), (1, 1), (W, H), bounds_type=2),
    scene_item("Cosmic Sky", ids["cosmic"], 2, (0, 0), (1, 1), (W, H), bounds_type=2),
    scene_item("Privacy Mask", ids["privacy"], 3, (0, 0), (1, 1), visible=False),
    scene_item("Stream Logo", ids["logo"], 4, (48, 48), (0.33, 0.33)),
    scene_item("Brand Bar (Live)", ids["brand_live"], 5, (0, 1305), (0.926, 0.926)),
    scene_item("Holographic Orb", ids["orb"], 6, (0, 0), (1, 1)),
]

soon_items = [
    scene_item("Display Capture", display_id, 1, (0, 0), (1, 1), (W, H), bounds_type=2),
    scene_item("Soon Backdrop", ids["soon_bg"], 2, (0, 0), (1, 1), (W, H), bounds_type=2),
    scene_item("Stream Logo", ids["logo"], 3, (48, 48), (0.33, 0.33)),
    scene_item("Holographic Orb", ids["orb"], 4, (0, 0), (1, 1)),
    scene_item("Brand Bar (Soon)", ids["brand_soon"], 5, (0, 1305), (0.926, 0.926)),
]

display_src = {
    "prev_ver": 503382018,
    "name": "Display Capture",
    "uuid": display_id,
    "id": "display_capture",
    "versioned_id": "display_capture",
    "settings": {"capture_cursor": True},
    "mixers": 0, "sync": 0, "flags": 0, "volume": 1.0, "balance": 0.5,
    "enabled": True, "muted": False,
    "push-to-mute": False, "push-to-mute-delay": 0,
    "push-to-talk": False, "push-to-talk-delay": 0,
    "hotkeys": {},
    "deinterlace_mode": 0, "deinterlace_field_order": 0, "monitoring_type": 0,
    "filters": [],
    "private_settings": {},
}
display_src["filters"] = [zoom_crop_filter()]

collection = {
    "current_scene": "Vibe Coding",
    "current_program_scene": "Vibe Coding",
    "scene_order": [{"name": "Starting Soon"}, {"name": "Vibe Coding"}],
    "name": "Nebula Vibe Desk",
    "sources": [
        display_src,
        browser("Cosmic Sky", ids["cosmic"], "overlays/cosmic-sky.html", W, H, COSMIC_CSS),
        browser("Privacy Mask", ids["privacy"], "overlays/privacy-blur.html", W, H),
        image_logo("Stream Logo", ids["logo"], BRANDING.get("logoOpacity", 0.52)),
        browser("Brand Bar (Live)", ids["brand_live"], "overlays/brandbar.html?mode=live", 720, 90),
        browser("Holographic Orb", ids["orb"], f"http://127.0.0.1:{BRIDGE_PORT}/overlays/orb.html", W, H, local=False),
        browser("Soon Backdrop", ids["soon_bg"], "overlays/soon-backdrop.html", W, H),
        browser("Brand Bar (Soon)", ids["brand_soon"], "overlays/brandbar.html?mode=soon", 720, 90),
        make_scene("Vibe Coding", ids["scene_vibe"], MAIN_CANVAS_UUID, vibe_items),
        make_scene("Starting Soon", ids["scene_soon"], MAIN_CANVAS_UUID, soon_items),
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
OUT.write_text(json.dumps(collection, indent=4), encoding="utf-8")
print(f"wrote {OUT}")
