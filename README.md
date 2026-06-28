# TonkaToyXL OBS Templates

Free OBS overlays and scene packs from [TonkaToyXL](https://github.com/TonkaToyXL) streams. No signup — download, unzip, double-click install.

**Share this link:** `https://github.com/TonkaToyXL/obs-templates`

## Download

| Template | What it is | Download | OBS |
|----------|------------|----------|-----|
<!-- DOWNLOADS:START -->
| **Nebula Vibe Desk** | Full-screen cosmic sky, shooting stars, moon, and voice-reactive holographic orb with local health and config panels. | [Download `nebula-vibe-desk-v2.1.0.zip`](./dist/nebula-vibe-desk-v2.1.0.zip) (277 KB) | 30.0 |
<!-- DOWNLOADS:END -->

## Preview

**Nebula Vibe Desk v2.1.0**

![Nebula Vibe Coding scene preview](./templates/nebula-vibe-desk/docs/previews/vibe-coding.webp)

| Starting Soon | Local config panel |
|---------------|--------------------|
| ![Nebula Starting Soon scene preview](./templates/nebula-vibe-desk/docs/previews/starting-soon.webp) | ![Nebula config panel preview](./templates/nebula-vibe-desk/docs/previews/config-panel.webp) |

Each zip is **plug-and-play**:

1. Download → unzip  
2. Double-click **`install.command`** (Mac) or **`Install.bat`** (Windows)  
3. OBS → **Scene Collection** → **nebula-vibe-desk** → **Vibe Coding**

## What's fixed vs customizable

| Included (core) | You customize |
|-----------------|---------------|
| Cosmic sky, moon, shooting stars | `assets/logo.png` |
| Holographic voice-reactive orb | Local config page or `branding.user.json` |
| Vibe Coding + Starting Soon scenes | Mic choice & audio filters in OBS |

## Requirements

- [OBS Studio](https://obsproject.com/) 30+
- Python 3. The installer creates a local bridge venv for `websockets`
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
