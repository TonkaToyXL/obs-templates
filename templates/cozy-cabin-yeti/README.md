# Cozy Cabin Yeti

Warm snowy cabin coding scene with fireplace edge glow, snowfall, and a friendly mic-reactive Yeti orb.  
Download from [TonkaToyXL/obs-templates](https://github.com/TonkaToyXL/obs-templates).

## Preview

**Current preview: v1.1.1**

![Cozy Cabin Yeti Vibe Coding scene preview](docs/previews/vibe-coding.webp)

| Starting Soon | Local config panel |
|---------------|--------------------|
| ![Cozy Cabin Yeti Starting Soon scene preview](docs/previews/starting-soon.webp) | ![Cozy Cabin Yeti config panel preview](docs/previews/config-panel.webp) |

## Install (double-click)

| Platform | File |
|----------|------|
| **Mac** | `install.command` |
| **Windows** | `Install.bat` |

On Mac, installs the runtime to `~/Library/Application Support/OBS-Templates/cozy-cabin-yeti/`, registers the OBS scene collection, and starts the mic bridge with LaunchAgent.

**In OBS:** Scene Collection → **Cozy Cabin Yeti** → scene **Vibe Coding**.

## What's included (core — don't need to touch)

| Layer | File | Role |
|-------|------|------|
| Cabin Overlay | `overlays/cabin.html` | Transparent wood frame, snowy window, fireplace glow |
| Yeti Voice Orb | `overlays/orb.html` | Mic-reactive friendly Yeti |
| Privacy Mask | `overlays/privacy-blur.html` | Optional top/bottom blur (off by default) |
| Bridge | `bridge/orb-bridge.py` | Serves overlays + `/level.json` mic levels |
| Health + Config | `overlays/health.html`, `overlays/config.html` | Local diagnostics and tuning |

## Customize (your brand)

Open **`http://127.0.0.1:8766/config.html`** after install, or edit **`branding.user.json`** (copy from `branding.user.example.json`):

| Key | What it does |
|-----|----------------|
| `brandName` | Brand bar wordmark |
| `tagLine` | Tag after LIVE pill (e.g. `cozy coding`) |
| `logoFile` | Relative path to stream logo (default `assets/logo.png`) |
| `logoOpacity` | Stream logo opacity (0–1) — applied live to OBS when bridge + OBS are running |
| `accentCyan` / `accentViolet` | Brand accents (snow / ember) |
| `bridgePort` | Local bridge port (default `8766`) |
| `micInputName` | Exact OBS audio source name (optional) |
| `orbPosition` | Preset: `lowerRight`, `rightEdge`, `centerRight`, or `lowerCenter` |
| `orbScale` | Whole-orb size multiplier (0.72–1.4) |
| `voiceSensitivity` | Orb/mouth response multiplier (0.45–2.4) |
| `glowIntensity` | Voice glow multiplier (0.45–1.8) |

Replace **`assets/logo.png`** with your logo (512×512 PNG recommended), or set `logoFile` in config.

If the Yeti does not react to your voice, set **Mic Input** in config to the exact OBS audio source name, then check health.

## Mic bridge

The orb reads levels from `http://127.0.0.1:8766/level.json`.
The local health panel is `http://127.0.0.1:8766/health.html`.
The local config panel is `http://127.0.0.1:8766/config.html`.

```bash
cd ~/Library/Application\ Support/OBS-Templates/cozy-cabin-yeti
./bridge/start-bridge.sh
```

**Mac auto-start:** `install.command` writes `~/Library/LaunchAgents/com.cozy-cabin-yeti.bridge.plist` automatically.

**Windows auto-start:** Double-click `bridge\start-bridge.bat`, or create a Task Scheduler login task that runs it with the install folder as the working directory.

## Audio

The scene includes a **Mic** source (default device). Suggested filter chain for spoken streams:

1. Noise suppression  
2. Noise gate  
3. Compressor  
4. Makeup gain (+10 to +13 dB)  
5. **Limiter last** (−2 dB ceiling)

Target **−16 LUFS** integrated for streaming.

## Scenes

- **Vibe Coding** — display + cabin frame + logo + brand bar + Yeti + mic  
- **Starting Soon** — cabin backdrop + logo + soon brand bar + Yeti + mic  

## Requirements

- OBS Studio 30+
- Python 3. The installer creates a local bridge venv and installs `websockets` there.
- WebSocket enabled: OBS → Settings → WebSocket

## Fonts

Bundled **Syne** and **JetBrains Mono** are SIL Open Font License (OFL). See [LICENSES.md](../../LICENSES.md).

## Privacy

Everything stays local. The bridge talks to OBS on `127.0.0.1`, serves local overlay files, and never sends mic levels or config anywhere.

## License

MIT — use freely. Credit appreciated.
