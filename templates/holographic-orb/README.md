# Holographic Voice-Reactive Orb

Free OBS browser overlay. The orb glows and pulses when you talk.

**Requires:** OBS 30+, [obs-websocket](https://github.com/obsproject/obs-websocket) enabled (built into OBS 28+).

## Install (2 minutes)

1. **Unzip** this folder anywhere permanent (e.g. `Documents/OBS-Templates/holographic-orb/`).
2. Open **OBS** → **Settings** → **WebSocket** → enable server (default port `4455`). Set a password if you want — then edit `CONFIG.wsPassword` in `overlays/orb.html`.
3. **Sources** → **+** → **Browser** → name it `Holographic Orb`.
4. Check **Local file**, browse to `overlays/orb.html`.
5. Set size to **400×400** (or scale to taste). Position bottom-right or wherever you like.
6. **Optional:** replace `assets/avatar.png` with your channel logo (1024×1024 PNG with transparency works best).
7. **Optional:** set `CONFIG.micInputName` in `overlays/orb.html` to your exact mic name (OBS → Audio Mixer → gear icon → name). Leave blank to auto-pick the first audio input.

## Mic not reacting?

1. Confirm WebSocket is on in OBS Settings.
2. Refresh the browser source (right-click → **Refresh cache of current page**).
3. Set `CONFIG.debug = true` in `orb.html`, refresh again — status text shows connection + mic level.

## Customize

Edit the `CONFIG` block at the top of `overlays/orb.html`:

- `accentCyan` / `accentViolet` — orb colors
- `micInputName` — your mic's OBS input name
- `wsPort` / `wsPassword` — WebSocket connection
