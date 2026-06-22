# TonkaToyXL OBS Templates

[![CI](https://github.com/TonkaToyXL/obs-templates/actions/workflows/ci.yml/badge.svg)](https://github.com/TonkaToyXL/obs-templates/actions/workflows/ci.yml)

Free OBS overlays and scene packs from [TonkaToyXL](https://github.com/TonkaToyXL) streams. No signup — download, unzip, double-click install.

**Share this link:** `https://github.com/TonkaToyXL/obs-templates`

## Download

| Template | What it is | Download | OBS |
|----------|------------|----------|-----|
<!-- DOWNLOADS:START -->
| **Nebula Vibe Desk** | Full-screen cosmic sky, shooting stars, moon, and voice-reactive holographic orb — your logo and brand bar are yours to customize. | [Download `nebula-vibe-desk-v2.0.0.zip`](./dist/nebula-vibe-desk-v2.0.0.zip) (200 KB) | 30.0 |
<!-- DOWNLOADS:END -->

Each zip is **plug-and-play**:

1. Download → unzip  
2. Double-click **`install.command`** (Mac) or **`Install.bat`** (Windows)  
3. OBS → **Scene Collection** → **nebula-vibe-desk** → **Vibe Coding**

## What's fixed vs customizable

| Included (core) | You customize |
|-----------------|---------------|
| Cosmic sky, moon, shooting stars | `assets/logo.png` |
| Holographic voice-reactive orb | `branding.user.json` (name, tag, colors) |
| Vibe Coding + Starting Soon scenes | Mic choice & audio filters in OBS |

## Requirements

- [OBS Studio](https://obsproject.com/) 30+
- Python 3 + `websockets` for the mic bridge
- WebSocket enabled: OBS → **Settings** → **WebSocket**

## Develop / package

```bash
./scripts/build-scene.py
./scripts/generate-installers.sh
./scripts/validate.sh
./scripts/package.sh nebula-vibe-desk
```

## License

MIT — use freely on your streams.

See [SECURITY.md](./SECURITY.md). Templates connect to OBS on your machine only (`127.0.0.1`).
