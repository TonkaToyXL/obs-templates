# Nebula Vibe Desk

Full-screen **cosmic sky** (stars, moon, shooting stars) + **voice-reactive holographic orb** for vibe-coding streams.  
Download from [TonkaToyXL/obs-templates](https://github.com/TonkaToyXL/obs-templates).

## Install (double-click)

| Platform | File |
|----------|------|
| **Mac** | `install.command` |
| **Windows** | `Install.bat` |

Installs to `Documents/OBS-Templates/nebula-vibe-desk/`, registers the OBS scene collection, and starts the mic bridge.

**In OBS:** Scene Collection → **nebula-vibe-desk** → scene **Vibe Coding**.

## What's included (core — don't need to touch)

| Layer | File | Role |
|-------|------|------|
| Cosmic Sky | `overlays/cosmic-sky.html` | Full-screen stars, moon, shooting stars |
| Holographic Orb | `overlays/orb.html` | Voice-reactive avatar — gentle hover float, subtle gaze, mic-driven mouth |
| Privacy Mask | `overlays/privacy-blur.html` | Optional top/bottom menu-bar blur (off by default) |
| Bridge | `bridge/orb-bridge.py` | Serves overlays + `/level.json` mic levels |

## Customize (your brand)

Edit **`branding.user.json`** (copy from `branding.user.example.json`):

| Key | What it does |
|-----|----------------|
| `brandName` | Brand bar wordmark |
| `tagLine` | Tag after LIVE pill (e.g. `vibe coding`) |
| `logoOpacity` | Stream logo opacity (0–1) |
| `accentCyan` / `accentViolet` | Brand bar accent colors |
| `micInputName` | Your mic name in OBS (optional) |

Replace **`assets/logo.png`** with your logo (512×512 PNG recommended).

Re-run `install.command` or restart the bridge after edits.

**Holographic Orb (OBS):** browser source must be **2560×1440** at position **0,0** (full canvas). After updating `orb.html`, right-click the source → **Refresh**.

## Mic bridge

The orb reads levels from `http://127.0.0.1:8765/level.json`.

```bash
cd ~/Documents/OBS-Templates/nebula-vibe-desk
./bridge/start-bridge.sh
```

**Mac auto-start:** copy `bridge/com.nebula-vibe-desk.bridge.plist.example` to `~/Library/LaunchAgents/`, replace `REPLACE_WITH_INSTALL_DIR`, then `launchctl load`.

## Audio (not in scene file)

Add your mic in OBS. Suggested filter chain for spoken streams:

1. Noise suppression  
2. Noise gate  
3. Compressor  
4. Makeup gain (+10 to +13 dB)  
5. **Limiter last** (−2 dB ceiling)

Target **−16 LUFS** integrated for streaming.

## Scenes

- **Vibe Coding** — display + cosmic sky + logo + brand bar + orb  
- **Starting Soon** — backdrop + logo + soon brand bar + orb  

## Requirements

- OBS Studio 30+
- Python 3 + `websockets` (`pip3 install websockets`)
- WebSocket enabled: OBS → Settings → WebSocket

## License

MIT — use freely. Credit appreciated.
