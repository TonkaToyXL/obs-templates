#!/usr/bin/env bash
# Generate per-template install.command, Install.bat, install.py, and install-guide.html
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES="$ROOT/templates"
INSTALLER_PY="$ROOT/scripts/installer.py"

write_mac_launcher() {
  local dir="$1"
  local name="$2"
  cat > "$dir/install.command" <<EOF
#!/bin/bash
cd "\$(dirname "\$0")"
echo "Installing $name..."
if command -v python3 >/dev/null 2>&1; then
  python3 install.py
else
  echo "Python 3 required. Install from python.org or use manual steps in README.md"
  exit 1
fi
echo
read -r -p "Press Enter to close..."
EOF
  chmod +x "$dir/install.command"
}

write_windows_launcher() {
  local dir="$1"
  local name="$2"
  cat > "$dir/Install.bat" <<EOF
@echo off
cd /d "%~dp0"
echo Installing $name...
where py >nul 2>nul && (py -3 install.py) || (where python >nul 2>nul && (python install.py) || (
  echo Python 3 required. See README.md for manual install.
  pause
  exit /b 1
))
echo.
pause
EOF
}

generate_guide() {
  local dir="$1"
  local id="$2"
  python3 - "$dir" "$id" <<'PY'
import json, html, sys
from pathlib import Path

dir_path = Path(sys.argv[1])
manifest = json.loads((dir_path / "manifest.json").read_text())
branding_path = dir_path / "branding.json"
branding = json.loads(branding_path.read_text()) if branding_path.exists() else {}
name = manifest["name"]
install_type = manifest.get("installType", "overlay")
port = int(branding.get("bridgePort", 8765) or 8765)
origin = f"http://127.0.0.1:{port}"
accent_cyan = str(branding.get("accentCyan") or "#00abfd")
accent_violet = str(branding.get("accentViolet") or "#7c4dff")
has_logo_asset = (dir_path / "assets" / "logo.png").exists()
custom_body = (
    f"Use <code>{origin}/config.html</code>, or replace <code>assets/logo.png</code> "
    "and edit <code>branding.user.json</code> (copy from <code>branding.user.example.json</code>)."
    if has_logo_asset
    else f"Use <code>{origin}/config.html</code>, or edit <code>branding.user.json</code> "
    "(copy from <code>branding.user.example.json</code>)."
)

def hex_to_rgb(value: str) -> tuple[int, int, int]:
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        return (0, 171, 253)
    try:
        n = int(text, 16)
    except ValueError:
        return (0, 171, 253)
    return ((n >> 16) & 255, (n >> 8) & 255, n & 255)

cr, cg, cb = hex_to_rgb(accent_cyan)
vr, vg, vb = hex_to_rgb(accent_violet)
cyan_rgb = f"{cr},{cg},{cb}"
violet_rgb = f"{vr},{vg},{vb}"
# Dark button text: prefer near-black on bright accents
btn_fg = "#00131f" if (cr * 299 + cg * 587 + cb * 114) / 1000 > 140 else "#f7fbff"

steps_overlay = [
    ("Download & unzip", "Get the zip from GitHub. Unzip anywhere.", "one click on the repo"),
    ("Double-click install", "Mac: <code>install.command</code><br>Windows: <code>Install.bat</code>", "installs runtime + opens OBS"),
    ("Pick the scene", "OBS > <strong>Scene Collection</strong> > your template > scene <strong>Vibe Coding</strong>.", "one menu pick"),
    ("Check health", f"Open <code>{origin}/health.html</code> to verify the bridge, OBS, mic, and meter. Open <code>{origin}/config.html</code> for local tuning.", "local diagnostics"),
    ("Talk", "Mic reactive orb lights up when you speak. WebSocket stays local to this machine.", "127.0.0.1 only"),
]
steps_scene = [
    ("Download & unzip", "Get the zip from GitHub.", "free / no account"),
    ("Double-click install", "Mac: <code>install.command</code> / Windows: <code>Install.bat</code>", "installs runtime + opens OBS"),
    ("Pick the scene", f"OBS > <strong>Scene Collection</strong> > <strong>{html.escape(name)}</strong> > <strong>Vibe Coding</strong>.", "orb source is ready"),
    ("Check health", f"Open <code>{origin}/health.html</code> to verify the bridge, OBS, mic, and meter. Open <code>{origin}/config.html</code> for local tuning.", "local diagnostics"),
    ("Customize your brand", custom_body, "optional"),
]
steps = steps_scene if install_type == "scene-collection" else steps_overlay

slides = ""
for i, (title, body, tag) in enumerate(steps, 1):
    slides += f"""
    <section class="slide" data-step="{i}">
      <div class="slide-top">
        <span class="step-pill">STEP {i:02d}</span>
        <span class="step-tag">{html.escape(tag)}</span>
      </div>
      <h2>{html.escape(title)}</h2>
      <p class="body">{body}</p>
    </section>"""

out = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Install - {html.escape(name)}</title>
  <style>
    @font-face {{
      font-family: "Syne";
      src: url("../fonts/Syne-Variable.ttf") format("truetype");
      font-weight: 600 800;
      font-style: normal;
      font-display: swap;
    }}
    @font-face {{
      font-family: "JetBrains Mono";
      src: url("../fonts/JetBrainsMono-Variable.ttf") format("truetype");
      font-weight: 400 700;
      font-style: normal;
      font-display: swap;
    }}
    :root {{
      --cyan: {html.escape(accent_cyan)};
      --violet: {html.escape(accent_violet)};
      --cyan-rgb: {cyan_rgb};
      --violet-rgb: {violet_rgb};
      --btn-fg: {btn_fg};
      --bg: #05080d;
      --panel: rgba(12,17,25,0.88);
      --panel-strong: #101722;
      --line: rgba(232,244,255,0.10);
      --text: #e8f4ff;
      --muted: #8aa0b8;
      --soft: #b8c7d9;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ background: var(--bg); overflow-x: hidden; }}
    body {{
      font-family: "Syne", system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      padding: 32px 20px 40px;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      background:
        radial-gradient(ellipse 72% 44% at 18% 0%, rgba(var(--cyan-rgb),0.11), transparent 56%),
        radial-gradient(ellipse 60% 44% at 88% 100%, rgba(var(--violet-rgb),0.13), transparent 52%),
        linear-gradient(rgba(232,244,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(232,244,255,0.025) 1px, transparent 1px);
      background-size: auto, auto, 32px 32px, 32px 32px;
      pointer-events: none;
      z-index: 0;
    }}
    body::after {{
      content: "";
      position: fixed;
      inset: 0;
      background: radial-gradient(ellipse 70% 72% at 50% 44%, transparent 0%, rgba(0,0,0,0.35) 100%);
      pointer-events: none;
      z-index: 0;
    }}
    .deck {{ position: relative; z-index: 1; width: 100%; max-width: 760px; margin: 0 auto; }}
    .header {{
      display: grid;
      gap: 14px;
      margin-bottom: 20px;
      padding: 18px 0 22px;
      border-bottom: 1px solid var(--line);
    }}
    .brand-fallback {{
      display: inline-flex;
      width: fit-content;
      align-items: center;
      gap: 10px;
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--cyan);
    }}
    .brand-fallback::before {{
      content: "";
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--cyan);
      box-shadow: 0 0 14px rgba(var(--cyan-rgb),0.75);
    }}
    .pack-title {{
      font-size: clamp(34px, 6vw, 56px);
      font-weight: 800;
      color: var(--text);
      line-height: 0.95;
      letter-spacing: 0;
      overflow-wrap: break-word;
    }}
    .sub {{
      max-width: 58ch;
      font-family: "JetBrains Mono", ui-monospace, monospace;
      font-size: 13px;
      line-height: 1.7;
      color: var(--muted);
      letter-spacing: 0;
      overflow-wrap: break-word;
    }}
    .sub em {{ color: var(--cyan); font-style: normal; }}
    .badge-row {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 2px; }}
    .badge {{
      font-family: "JetBrains Mono", ui-monospace, monospace;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 7px 9px;
      border-radius: 4px;
      border: 1px solid var(--line);
      color: var(--muted);
      background: rgba(232,244,255,0.025);
    }}
    .badge.live {{ border-color: rgba(var(--cyan-rgb),0.42); color: var(--cyan); }}
    .slide {{
      display: none;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 28px;
      position: relative;
      min-height: 230px;
      box-shadow: 0 18px 52px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.045);
      overflow: hidden;
    }}
    .slide::before {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        linear-gradient(100deg, rgba(var(--cyan-rgb),0.08), transparent 44%),
        radial-gradient(circle at 92% 10%, rgba(var(--violet-rgb),0.13), transparent 30%);
      pointer-events: none;
    }}
    .slide::after {{
      content: "";
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      height: 2px;
      background: linear-gradient(90deg, var(--cyan), var(--violet), transparent 82%);
      opacity: 0.86;
    }}
    .slide.active {{ display: block; animation: fade 0.22s ease; }}
    @keyframes fade {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
    .slide-top {{
      position: relative;
      z-index: 1;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 26px;
      gap: 16px;
    }}
    .step-pill {{
      font-family: "JetBrains Mono", ui-monospace, monospace;
      font-size: 12px;
      font-weight: 700;
      color: var(--btn-fg);
      background: var(--cyan);
      padding: 7px 10px;
      border-radius: 4px;
      letter-spacing: 0.08em;
      white-space: nowrap;
    }}
    .step-tag {{
      font-family: "JetBrains Mono", ui-monospace, monospace;
      font-size: 12px;
      color: var(--cyan);
      opacity: 0.82;
      text-align: right;
    }}
    h2 {{
      position: relative;
      z-index: 1;
      font-size: clamp(28px, 5vw, 42px);
      font-weight: 800;
      letter-spacing: 0;
      line-height: 1.05;
      margin-bottom: 14px;
      overflow-wrap: break-word;
    }}
    .body {{
      position: relative;
      z-index: 1;
      max-width: 62ch;
      font-size: 17px;
      line-height: 1.65;
      color: var(--soft);
      overflow-wrap: break-word;
    }}
    code {{
      font-family: "JetBrains Mono", ui-monospace, monospace;
      font-size: 0.86em;
      background: #101a26;
      color: var(--cyan);
      padding: 0.14em 0.38em;
      border-radius: 3px;
      border: 1px solid rgba(var(--cyan-rgb),0.22);
    }}
    .nav {{
      display: flex;
      gap: 12px;
      margin-top: 16px;
      align-items: center;
    }}
    button {{
      min-width: 92px;
      font-family: "Syne", system-ui, sans-serif;
      background: var(--cyan);
      color: var(--btn-fg);
      border: 1px solid rgba(var(--cyan-rgb),0.46);
      font-weight: 800;
      font-size: 14px;
      padding: 11px 16px;
      border-radius: 6px;
      cursor: pointer;
      transition: transform 0.12s, border-color 0.12s, background 0.12s, color 0.12s;
    }}
    button:hover:not(:disabled) {{ transform: translateY(-1px); }}
    button:active:not(:disabled) {{ transform: translateY(1px); }}
    button:focus-visible {{ outline: 2px solid var(--violet); outline-offset: 3px; }}
    button#prev {{
      background: rgba(232,244,255,0.04);
      color: var(--text);
      border-color: var(--line);
    }}
    button#next {{
      background: rgba(232,244,255,0.04);
      color: var(--text);
      border-color: var(--line);
    }}
    button#next:hover:not(:disabled), button#prev:hover:not(:disabled) {{ border-color: var(--cyan); color: var(--cyan); }}
    button#next.is-done {{ background: var(--cyan); color: var(--btn-fg); border-color: var(--cyan); }}
    button:disabled {{ opacity: 0.32; cursor: default; }}
    .dots {{ display: flex; gap: 7px; flex: 1; justify-content: center; }}
    .dot {{
      width: 34px;
      height: 3px;
      border-radius: 999px;
      background: rgba(232,244,255,0.12);
      transition: background 0.2s, box-shadow 0.2s, width 0.2s;
    }}
    .dot.active {{
      width: 54px;
      background: var(--cyan);
      box-shadow: 0 0 12px rgba(var(--cyan-rgb),0.45);
    }}
    .footer {{
      margin-top: 22px;
      padding-top: 16px;
      border-top: 1px solid var(--line);
      font-family: "JetBrains Mono", ui-monospace, monospace;
      font-size: 12px;
      color: var(--muted);
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
    }}
    a {{ color: var(--cyan); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    @media (max-width: 560px) {{
      body {{ padding: 22px 14px 28px; }}
      .deck {{ max-width: 362px; margin: 0; }}
      .pack-title {{ font-size: 32px; line-height: 1; }}
      .slide {{ padding: 22px 18px; min-height: 260px; }}
      h2 {{ font-size: 26px; line-height: 1.12; }}
      .body {{ font-size: 16px; }}
      .slide-top {{ align-items: flex-start; flex-direction: column; gap: 10px; }}
      .step-tag {{ text-align: left; }}
      .nav {{ gap: 8px; }}
      button {{ min-width: 76px; padding-inline: 12px; }}
      .dot {{ width: 22px; }}
      .dot.active {{ width: 36px; }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .slide.active {{ animation: none; }}
      button, .dot {{ transition: none; }}
    }}
  </style>
</head>
<body>
  <div class="deck">
    <header class="header">
      <div class="brand-fallback">OBS Template</div>
      <div class="pack-title">{html.escape(name)}</div>
      <p class="sub">Local install guide. Mac runtime: <em>~/Library/Application Support/OBS-Templates</em>. Health/config: <em>127.0.0.1:{port}</em>.</p>
      <div class="badge-row">
        <span class="badge live">browser source</span>
        <span class="badge">obs {html.escape(manifest.get("obsMinVersion", "30+"))}</span>
        <span class="badge">local bridge</span>
      </div>
    </header>
    {slides}
    <div class="nav">
      <button id="prev" disabled>Back</button>
      <div class="dots" id="dots"></div>
      <button id="next">Next</button>
    </div>
    <footer class="footer">
      <span>Install stays on this machine. Bridge starts with LaunchAgent on Mac.</span>
      <a href="https://github.com/TonkaToyXL/obs-templates">Source repo</a>
    </footer>
  </div>
  <script>
    const slides = [...document.querySelectorAll(".slide")];
    const dots = document.getElementById("dots");
    let i = 0;
    slides.forEach((_, j) => {{
      const d = document.createElement("div");
      d.className = "dot" + (j === 0 ? " active" : "");
      dots.appendChild(d);
    }});
    function show(n) {{
      i = Math.max(0, Math.min(n, slides.length - 1));
      slides.forEach((s, j) => s.classList.toggle("active", j === i));
      [...dots.children].forEach((d, j) => d.classList.toggle("active", j === i));
      document.getElementById("prev").disabled = i === 0;
      const nxt = document.getElementById("next");
      const done = i === slides.length - 1;
      nxt.textContent = done ? "Done" : "Next";
      nxt.classList.toggle("is-done", done);
    }}
    document.getElementById("prev").onclick = () => show(i - 1);
    document.getElementById("next").onclick = () => show(i < slides.length - 1 ? i + 1 : i);
    document.addEventListener("keydown", e => {{
      if (e.key === "ArrowRight") document.getElementById("next").click();
      if (e.key === "ArrowLeft") document.getElementById("prev").click();
    }});
    show(0);
  </script>
</body>
</html>"""

(dir_path / "docs").mkdir(parents=True, exist_ok=True)
(dir_path / "docs" / "install-guide.html").write_text(out, encoding="utf-8")
print(f"  guide: {dir_path.name}/docs/install-guide.html")
PY
}

"$ROOT/scripts/sync-shared.sh"

shopt -s nullglob
for dir in "$TEMPLATES"/*/; do
  id="$(basename "$dir")"
  [[ "$id" == _* ]] && continue
  [[ -f "$dir/manifest.json" ]] || continue

  cp "$INSTALLER_PY" "$dir/install.py"
  mkdir -p "$dir/docs"
  name="$(python3 - "$dir/manifest.json" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["name"])
PY
)"
  write_mac_launcher "$dir" "$name"
  write_windows_launcher "$dir" "$name"
  generate_guide "$dir" "$id"
  echo "installers: $id"
done
