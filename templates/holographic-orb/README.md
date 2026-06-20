# Holographic Voice-Reactive Orb

Free OBS browser overlay — **no channel branding on stream**. Cosmic glow + mic-reactive pulse. Make it yours via `CONFIG` in `overlays/orb.html`.

Downloaded from [TonkaToyXL/obs-templates](https://github.com/TonkaToyXL/obs-templates).

## Install (double-click)

| Platform | File |
|----------|------|
| **Mac** | `install.command` |
| **Windows** | `Install.bat` |

Files install to `Documents/OBS-Templates/holographic-orb/`. A walkthrough opens in your browser.

OBS: **Sources → + → Browser** → **Local file** → `overlays/orb.html`.

## Customize (your brand)

Edit the `CONFIG` block at the top of `overlays/orb.html`:

| Setting | What it does |
|---------|----------------|
| `logoFile` | Path to your logo (`../assets/your-logo.png`) |
| `showLogo` | `false` = pure cosmic orb, no center image |
| `accentWarm` / `accentCyan` / `accentViolet` | Orb colors |
| `micInputName` | Your mic name in OBS (blank = auto-detect) |
| `wsPassword` | Only if you set a WebSocket password in OBS |

Replace `assets/avatar.svg` with your own PNG/SVG, or set `showLogo: false`.

## Requirements

- OBS Studio 30+
- WebSocket: **OBS → Settings → WebSocket**

## Video walkthrough

_Coming soon._
