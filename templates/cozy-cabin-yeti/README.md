# Cozy Cabin Yeti

Free OBS scene collection for a warm cabin coding stream: snowy window, fireplace glow, soft privacy bands, and a friendly mic-reactive Yeti orb.

## What ships

- **Vibe Coding** scene with display capture, animated cabin frame, brand bar, optional privacy mask, and Yeti orb
- **Starting Soon** scene with snowy cabin window, fireplace animation, Yeti orb, and brand bar
- Local bridge on `127.0.0.1:8766` for `/level.json`, health, and config pages
- Text brand controls, mic input override, orb position, scale, voice sensitivity, and glow tuning

## Install

| Platform | What to double-click |
|----------|----------------------|
| Mac | `install.command` |
| Windows | `Install.bat` |

Then open OBS and choose **Scene Collection -> Cozy Cabin Yeti -> Vibe Coding**.

If the Yeti does not react to your voice, open `http://127.0.0.1:8766/config.html` and set **Mic Input** to the exact OBS audio source name, then check `http://127.0.0.1:8766/health.html`.

## Sources

- `overlays/cabin.html` - transparent live-scene cabin edge overlay
- `overlays/orb.html` - mic-reactive friendly Yeti orb
- `overlays/brandbar.html` - lower-third stream brand bar
- `overlays/privacy-blur.html` - optional top/bottom privacy mask
- `overlays/soon-backdrop.html` - full starting-soon cabin scene

## Local controls

After install, open:

- Health: `http://127.0.0.1:8766/health.html`
- Config: `http://127.0.0.1:8766/config.html`

The bridge stays local on `127.0.0.1` and reads OBS mic levels through OBS WebSocket.

## Requirements

- OBS Studio 30+
- Python 3 for the installer and local mic bridge
- OBS WebSocket enabled in OBS Settings

## Privacy

Everything stays local. The bridge talks to OBS on `127.0.0.1`, serves local overlay files, and never sends mic levels or config anywhere.
