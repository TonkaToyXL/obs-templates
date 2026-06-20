#!/usr/bin/env python3
"""Generate minimal OBS scene collection for holographic-orb template."""
import json
import uuid
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "templates/holographic-orb/scene/holographic-orb.json"

sky_uuid = str(uuid.uuid4())
orb_uuid = str(uuid.uuid4())
scene_uuid = str(uuid.uuid4())
canvas_uuid = str(uuid.uuid4())

def browser_source(name, uid, local_file, w, h):
    return {
        "prev_ver": 536936449,
        "name": name,
        "uuid": uid,
        "id": "browser_source",
        "versioned_id": "browser_source",
        "settings": {
            "is_local_file": True,
            "local_file": local_file,
            "width": w,
            "height": h,
            "fps": 30,
            "shutdown": False,
            "restart_when_active": True,
            "css": "body { background-color: rgba(0,0,0,0); margin: 0; overflow: hidden; }",
            "reroute_audio": False,
        },
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

def scene_item(name, source_uuid, x, y, scale=1.0, item_id=1):
    return {
        "name": name,
        "source_uuid": source_uuid,
        "visible": True,
        "locked": False,
        "rot": 0.0,
        "scale_ref": {"x": 1920.0, "y": 1080.0},
        "align": 5,
        "bounds_type": 0,
        "bounds_align": 0,
        "bounds_crop": False,
        "crop_left": 0,
        "crop_top": 0,
        "crop_right": 0,
        "crop_bottom": 0,
        "id": item_id,
        "group_item_backup": False,
        "pos": {"x": float(x), "y": float(y)},
        "pos_rel": {"x": 0.0, "y": 0.0},
        "scale": {"x": scale, "y": scale},
        "scale_rel": {"x": scale, "y": scale},
        "bounds": {"x": 0.0, "y": 0.0},
        "bounds_rel": {"x": 0.0, "y": 0.0},
        "scale_filter": "disable",
        "blend_method": "default",
        "blend_type": "normal",
        "show_transition": {"duration": 0},
        "hide_transition": {"duration": 0},
        "private_settings": {},
    }

collection = {
    "current_scene": "Voice Orb",
    "current_program_scene": "Voice Orb",
    "scene_order": [{"name": "Voice Orb"}],
    "name": "holographic-orb",
    "sources": [
        browser_source("Cosmic Sky", sky_uuid, "{{INSTALL_DIR}}/overlays/cosmic-sky.html", 1920, 1080),
        browser_source("Holographic Orb", orb_uuid, "{{INSTALL_DIR}}/overlays/orb.html", 400, 400),
        {
            "prev_ver": 536936449,
            "name": "Voice Orb",
            "uuid": scene_uuid,
            "id": "scene",
            "versioned_id": "scene",
            "settings": {
                "items": [
                    scene_item("Cosmic Sky", sky_uuid, 0, 0, 1.0, 1),
                    scene_item("Holographic Orb", orb_uuid, 1480, 620, 1.0, 2),
                ],
                "custom_size": False,
                "id_counter": 3,
            },
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
            "canvas_uuid": canvas_uuid,
            "private_settings": {},
        },
    ],
    "groups": [],
    "quick_transitions": [],
    "transitions": [],
    "saved_projectors": [],
    "canvases": [{"info": {"name": "", "uuid": canvas_uuid, "private": False, "flags": 0}}],
    "current_transition": "Fade",
    "transition_duration": 300,
    "resolution": {"x": 1920, "y": 1080},
    "version": 2,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(collection, indent=2), encoding="utf-8")
print(f"wrote {OUT}")
