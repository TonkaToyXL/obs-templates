#!/usr/bin/env bash
# Generate per-template install.command, Install.bat, install.py, and install-guide.html
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES="$ROOT/templates"
INSTALLER_PY="$ROOT/scripts/installer.py"

write_mac_launcher() {
  local dir="$1"
  cat > "$dir/install.command" <<'EOF'
#!/bin/bash
cd "$(dirname "$0")"
echo "Installing Nebula Vibe Desk..."
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
  cat > "$dir/Install.bat" <<'EOF'
@echo off
cd /d "%~dp0"
echo Installing Nebula Vibe Desk...
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
  local brand="$ROOT/scripts/brand"
  cp "$brand/tonka-wordmark.svg" "$dir/docs/tonka-wordmark.svg" 2>/dev/null || true
  python3 - "$dir" "$id" <<'PY'
import json, html, sys
from pathlib import Path

dir_path = Path(sys.argv[1])
manifest = json.loads((dir_path / "manifest.json").read_text())
name = manifest["name"]
install_type = manifest.get("installType", "overlay")

steps_overlay = [
    ("Download & unzip", "Get the zip from GitHub. Unzip anywhere.", "one click on the repo"),
    ("Double-click install", "Mac → <code>install.command</code><br>Windows → <code>Install.bat</code>", "installs scene + opens OBS"),
    ("Pick the scene", "OBS → <strong>Scene Collection</strong> → your template → scene <strong>Vibe Coding</strong>.", "one menu pick"),
    ("Talk", "Mic reactive orb lights up when you speak. WebSocket is enabled locally for you.", "127.0.0.1 only — safe"),
]
steps_scene = [
    ("Download & unzip", "Get the zip from GitHub.", "free · no account"),
    ("Double-click install", "Mac → <code>install.command</code> · Windows → <code>Install.bat</code>", "installs scene + opens OBS"),
    ("Pick the scene", f"OBS → <strong>Scene Collection</strong> → <strong>{manifest['id']}</strong> → talk into your mic.", "orb reacts instantly"),
    ("Customize your brand", "Replace <code>assets/logo.png</code> and edit <code>branding.user.json</code> (copy from <code>branding.user.example.json</code>). Re-run install to refresh the brand bar.", "optional"),
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

wordmark = "tonka-wordmark.svg" if (dir_path / "docs/tonka-wordmark.svg").exists() else ""

out = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Install — {html.escape(name)} · TonkaToyXL</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --tonka: #f4b800;
      --tonka-dim: #c49200;
      --cyan: #3ee8ff;
      --violet: #a855f7;
      --bg: #080b12;
      --panel: #0f1419;
      --line: #1c2433;
      --text: #e8edf5;
      --muted: #8b9bb4;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: "Space Grotesk", system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      padding: 2rem 1.25rem 3rem;
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      background:
        radial-gradient(ellipse 80% 50% at 15% 0%, rgba(244,184,0,0.07), transparent 55%),
        radial-gradient(ellipse 60% 40% at 90% 100%, rgba(62,232,255,0.06), transparent 50%),
        linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
      background-size: auto, auto, 28px 28px, 28px 28px;
      pointer-events: none;
      z-index: 0;
    }}
    .deck {{ position: relative; z-index: 1; max-width: 680px; margin: 0 auto; }}
    .header {{
      margin-bottom: 1.75rem;
      padding-bottom: 1.25rem;
      border-bottom: 1px solid var(--line);
    }}
    .wordmark {{ height: 36px; width: auto; margin-bottom: 0.85rem; display: block; }}
    .brand-fallback {{
      font-size: 1.65rem;
      font-weight: 700;
      letter-spacing: -0.03em;
      margin-bottom: 0.85rem;
    }}
    .brand-fallback .t {{ color: var(--tonka); }}
    .brand-fallback .xl {{ color: var(--cyan); }}
    .pack-title {{
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--text);
      margin-bottom: 0.35rem;
    }}
    .sub {{
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.78rem;
      color: var(--muted);
      letter-spacing: 0.02em;
    }}
    .sub em {{ color: var(--tonka); font-style: normal; }}
    .badge-row {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.85rem; }}
    .badge {{
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.68rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      padding: 0.3rem 0.55rem;
      border-radius: 4px;
      border: 1px solid var(--line);
      color: var(--muted);
    }}
    .badge.live {{ border-color: rgba(244,184,0,0.45); color: var(--tonka); }}
    .slide {{
      display: none;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 1.75rem 1.5rem 1.5rem;
      position: relative;
      box-shadow: 0 16px 48px rgba(0,0,0,0.35);
    }}
    .slide::before, .slide::after {{
      content: "";
      position: absolute;
      width: 14px; height: 14px;
      border-color: var(--tonka);
      border-style: solid;
      opacity: 0.55;
    }}
    .slide::before {{ top: 10px; left: 10px; border-width: 2px 0 0 2px; }}
    .slide::after {{ bottom: 10px; right: 10px; border-width: 0 2px 2px 0; }}
    .slide.active {{ display: block; animation: fade 0.25s ease; }}
    @keyframes fade {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
    .slide-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      gap: 0.75rem;
    }}
    .step-pill {{
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--bg);
      background: var(--tonka);
      padding: 0.25rem 0.55rem;
      border-radius: 3px;
      letter-spacing: 0.06em;
    }}
    .step-tag {{
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.68rem;
      color: var(--cyan);
      opacity: 0.85;
    }}
    h2 {{
      font-size: 1.65rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      line-height: 1.2;
      margin-bottom: 0.85rem;
    }}
    .body {{
      font-size: 1rem;
      line-height: 1.65;
      color: #b8c5d9;
    }}
    code {{
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.86em;
      background: #161d28;
      color: var(--cyan);
      padding: 0.12em 0.38em;
      border-radius: 3px;
      border: 1px solid #243044;
    }}
    .nav {{
      display: flex;
      gap: 0.75rem;
      margin-top: 1.25rem;
      align-items: center;
    }}
    button {{
      font-family: "Space Grotesk", sans-serif;
      background: var(--tonka);
      color: #0a0c10;
      border: none;
      font-weight: 700;
      font-size: 0.9rem;
      padding: 0.7rem 1.25rem;
      border-radius: 6px;
      cursor: pointer;
      transition: transform 0.12s, box-shadow 0.12s;
      box-shadow: 0 4px 0 var(--tonka-dim);
    }}
    button:hover:not(:disabled) {{ transform: translateY(-1px); }}
    button:active:not(:disabled) {{ transform: translateY(2px); box-shadow: 0 1px 0 var(--tonka-dim); }}
    button#next {{
      background: transparent;
      color: var(--text);
      border: 1px solid var(--line);
      box-shadow: none;
    }}
    button#next:hover:not(:disabled) {{ border-color: var(--cyan); color: var(--cyan); }}
    button:disabled {{ opacity: 0.3; cursor: default; box-shadow: none; }}
    .dots {{ display: flex; gap: 6px; flex: 1; justify-content: center; }}
    .dot {{
      width: 7px; height: 7px; border-radius: 1px;
      background: #2a3448;
      transform: rotate(45deg);
      transition: background 0.2s, box-shadow 0.2s;
    }}
    .dot.active {{
      background: var(--tonka);
      box-shadow: 0 0 8px rgba(244,184,0,0.5);
    }}
    .footer {{
      margin-top: 1.5rem;
      padding-top: 1rem;
      border-top: 1px solid var(--line);
      font-family: "IBM Plex Mono", monospace;
      font-size: 0.72rem;
      color: var(--muted);
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}
    a {{ color: var(--cyan); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <div class="deck">
    <header class="header">
      {"<img class='wordmark' src='tonka-wordmark.svg' alt='TonkaToyXL' />" if wordmark else "<div class='brand-fallback'><span class='t'>Tonka</span>Toy<span class='xl'>XL</span></div>"}
      <div class="pack-title">{html.escape(name)}</div>
      <p class="sub">install walkthrough · <em>free</em> · built on stream</p>
      <div class="badge-row">
        <span class="badge live">vibe coding</span>
        <span class="badge">obs {html.escape(manifest.get("obsMinVersion", "30+"))}</span>
        <span class="badge">no signup</span>
      </div>
    </header>
    {slides}
    <div class="nav">
      <button id="prev" disabled>← back</button>
      <div class="dots" id="dots"></div>
      <button id="next">next →</button>
    </div>
    <footer class="footer">
      <span>github.com/TonkaToyXL/obs-templates</span>
      <a href="https://github.com/TonkaToyXL/obs-templates">download more</a>
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
      nxt.textContent = i === slides.length - 1 ? "done ✓" : "next →";
      nxt.style.background = i === slides.length - 1 ? "var(--tonka)" : "";
      nxt.style.color = i === slides.length - 1 ? "#0a0c10" : "";
      nxt.style.borderColor = i === slides.length - 1 ? "var(--tonka)" : "";
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

shopt -s nullglob
for dir in "$TEMPLATES"/*/; do
  id="$(basename "$dir")"
  [[ "$id" == _* ]] && continue
  [[ -f "$dir/manifest.json" ]] || continue

  cp "$INSTALLER_PY" "$dir/install.py"
  mkdir -p "$dir/docs"
  write_mac_launcher "$dir"
  write_windows_launcher "$dir"
  generate_guide "$dir" "$id"
  echo "installers: $id"
done
