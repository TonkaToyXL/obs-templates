# Changelog

All notable changes to the templates in this repo. Format: [Keep a Changelog](https://keepachangelog.com/). Versions are per-template (see each `manifest.json`).

## nebula-vibe-desk v2.3.0 — 2026-07-22

**Added — responsive canvas (1080p support):**

- The installer now detects your OBS base resolution (`BaseCX`/`BaseCY` from the active OBS profile) and scales the scene collection to fit: full-canvas browser sources resize, item positions/bounds follow, zoom crop filter and inline CSS scale too. Designed at 2560×1440; works at 1920×1080 and beyond.
- Overlays are resolution-independent: cosmic-sky fills its viewport (no more hardcoded 2560×1440), orb position presets are fractional (same spot on any canvas), soon-backdrop and privacy-blur are fluid.
- Opt-in via `responsiveCanvas: true` in the manifest (nebula only for now; cozy-cabin-yeti unchanged).
- New `tests/test_installer_canvas.py`: scaling + OBS profile detection coverage.

## nebula-vibe-desk v2.2.2 — 2026-07-22

**Changed:**

- Privacy Mask browser source now runs at **15 FPS** (the blur is static — 30 FPS wasted GPU).
- `manifest_validate.py` gains port-consistency validation: `bridgePort` in `branding.json` must match every `127.0.0.1` port referenced by the scene JSON, `orb.html`, and README — the drift class that once shipped a frozen orb is now blocked in `validate.sh`, CI, and pytest. Scene `{{INSTALL_DIR}}` paths are also checked against real files.
- Shared bridge: mic auto-pick skip list neutralized — removed device-specific hardware names and the `webcam` skip (a webcam mic may be a user's only input). Also shipped as **cozy-cabin-yeti v1.1.2**.

**Added:**

- This changelog.

## nebula-vibe-desk v2.2.1 — 2026-07-09

- Template hygiene and quality pass: shared pack (`templates/_shared/`) for bridge + privacy overlay across templates, `sync-shared.sh`, pytest suite, GitHub Actions CI.
- Hardened privacy validation: stream-key checks (#4), CI/privacy hardening (#6).
- Config tuning panel (`orbPosition`, `orbScale`, `voiceSensitivity`, `glowIntensity`) and `health.html` overlay; scoped CORS on the bridge.

## cozy-cabin-yeti v1.1.3 — 2026-07-22

- Shared privacy-blur overlay is now fluid (`100%` viewport) instead of hardcoded 2560×1440 — renders identically at native canvas, ready for responsive installs.

## cozy-cabin-yeti v1.1.2 — 2026-07-22

- Shared bridge pickup: neutralized mic auto-pick skip list (no device-specific names; webcam mics no longer skipped).

## cozy-cabin-yeti v1.1.1 — 2026-06-30

- New template: cozy cabin overlay + Yeti voice orb. Rendering hardening across templates.

## nebula-vibe-desk v2.1.0 — 2026-06-27

- Nebula config tuning panel; template preview assets; one versioned release zip per template in `dist/`.

## nebula-vibe-desk v2.0.0 — 2026-06-19

- Plug-and-play scene-collection installer (Mac + Windows), neutral on-stream branding via `branding.user.json`, install-guide slide deck, safe WebSocket setup.
