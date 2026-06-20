# Holographic Voice-Reactive Orb

Plug-and-play OBS scene — cosmic sky + mic-reactive orb. **No branding on your stream.** Customize colors and logo in `CONFIG`.

## Install (2 steps)

1. **Download** the zip from [GitHub](https://github.com/TonkaToyXL/obs-templates) and unzip
2. **Double-click** `install.command` (Mac) or `Install.bat` (Windows)

The installer copies files, registers the scene in OBS, enables local WebSocket, and opens OBS.

**In OBS:** Scene Collection → **holographic-orb** → scene **Voice Orb** → talk into your mic.

That's it.

## Customize

Edit `CONFIG` in `overlays/orb.html` — logo, colors, mic name.

| Setting | What it does |
|---------|----------------|
| `showLogo` | `false` = orb only, no center image |
| `logoFile` | Your PNG/SVG path |
| `accentWarm` / `accentCyan` / `accentViolet` | Orb colors |
| `wsPassword` | Only if you set a WebSocket password in OBS |

## Security

- Connects to OBS on **your computer only** (`127.0.0.1`)
- Installer enables local WebSocket for mic levels — no data sent online
- No stream keys, passwords, or personal info in the download

## Requirements

- OBS Studio 30+
