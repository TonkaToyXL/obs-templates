# Nebula Vibe Desk

Full-screen **cosmic sky** (stars, moon, shooting stars) + **voice-reactive holographic orb** for vibe-coding streams.  
Download from [TonkaToyXL/obs-templates](https://github.com/TonkaToyXL/obs-templates).

## Preview

**Current preview: v2.2.1**

![Nebula Vibe Coding scene preview](docs/previews/vibe-coding.webp)

| Starting Soon | Local config panel |
|---------------|--------------------|
| ![Nebula Starting Soon scene preview](docs/previews/starting-soon.webp) | ![Nebula config panel preview](docs/previews/config-panel.webp) |

## Install (double-click)

| Platform | File |
|----------|------|
| **Mac** | `install.command` |
| **Windows** | `Install.bat` |

On Mac, installs the runtime to `~/Library/Application Support/OBS-Templates/nebula-vibe-desk/`, registers the OBS scene collection, and starts the mic bridge with LaunchAgent. Existing `~/Documents/OBS-Templates/nebula-vibe-desk/` branding/logo files are migrated when present and left in place.

**In OBS:** Scene Collection → **Nebula Vibe Desk** → scene **Vibe Coding**.

## What's included (core — don't need to touch)

| Layer | File | Role |
|-------|------|------|
| Cosmic Sky | `overlays/cosmic-sky.html` | Full-screen stars, moon, shooting stars |
| Holographic Orb | `overlays/orb.html` | Voice-reactive avatar — gentle hover float, subtle gaze, mic-driven mouth |
| Privacy Mask | `overlays/privacy-blur.html` | Optional top/bottom menu-bar blur (off by default) |
| Bridge | `bridge/orb-bridge.py` | Serves overlays + `/level.json` mic levels |
| Health + Config | `overlays/health.html`, `overlays/config.html` | Local diagnostics and orb tuning |

## Customize (your brand)

Open **`http://127.0.0.1:18765/config.html`** after install, or edit **`branding.user.json`** (copy from `branding.user.example.json`):

| Key | What it does |
|-----|----------------|
| `brandName` | Brand bar wordmark |
| `tagLine` | Tag after LIVE pill (e.g. `vibe coding`) |
| `logoFile` | Relative path to stream logo (default `assets/logo.png`) |
| `logoOpacity` | Stream logo opacity (0–1) — applied live to OBS when bridge + OBS are running |
| `accentCyan` / `accentViolet` | Brand bar accent colors |
| `bridgePort` | Local bridge port (default `18765`) |
| `micInputName` | Your mic name in OBS (optional) |
| `orbPosition` | Preset: `lowerRight`, `rightEdge`, `centerRight`, or `lowerCenter` |
| `orbScale` | Whole-orb size multiplier (0.72–1.4) |
| `voiceSensitivity` | Orb/mouth response multiplier (0.45–2.4) |
| `glowIntensity` | Voice glow multiplier (0.45–1.8) |

Replace **`assets/logo.png`** with your logo (512×512 PNG recommended), or set `logoFile` in config.

Config page saves update `branding.user.json` and `overlays/branding.js`. When the bridge is connected to OBS, `logoFile` / `logoOpacity` also update the **Stream Logo** source live. If OBS is closed, config still saves — reopen OBS (or save config again after OBS is up) to apply logo changes.

**Holographic Orb (OBS):** browser source must be **2560×1440** at position **0,0** (full canvas). After updating `orb.html`, right-click the source → **Refresh**.

## Mic bridge

The orb reads levels from `http://127.0.0.1:18765/level.json`.
The local health panel is `http://127.0.0.1:18765/health.html`.
The local config panel is `http://127.0.0.1:18765/config.html`.

```bash
cd ~/Library/Application\ Support/OBS-Templates/nebula-vibe-desk
./bridge/start-bridge.sh
```

**Mac auto-start:** `install.command` writes `~/Library/LaunchAgents/com.nebula-vibe-desk.bridge.plist` automatically. The bridge reads OBS WebSocket auth from OBS's local config when needed, without storing secrets in the plist.

**Windows auto-start:** Double-click `bridge\start-bridge.bat`, or create a Task Scheduler login task that runs it with the install folder as the working directory.

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
- Python 3. The installer creates a local bridge venv and installs `websockets` there.
- WebSocket enabled: OBS → Settings → WebSocket

## Fonts

Bundled **Syne** and **JetBrains Mono** are SIL Open Font License (OFL). See [LICENSES.md](../../LICENSES.md).

## License

MIT — use freely. Credit appreciated.
