# For us — publishing templates

## Safety first (every time)

```bash
./scripts/sync-shared.sh # copy templates/_shared into each template
./scripts/validate.sh    # blocks personal paths, emails, secrets, bad manifests
./scripts/ship.sh "..."  # validate → installers → zip → push
```

**Never commit:** raw OBS JSON from your Mac (`/Users/...` paths), WebSocket passwords, stream keys, personal logos.

**Template vs hub branding:** Ship **neutral** overlays (no TonkaToyXL on-stream). Hub README + install guide can credit TonkaToyXL. Users customize via config / `branding.user.json`.

**Shared pack:** Edit `templates/_shared/` (bridge + privacy-blur), never only one template's copy. `package.sh` / `generate-installers.sh` run `sync-shared.sh` so zips stay self-contained. `~/Documents/OBS-Templates/` is a legacy path — App Support is the live install root on Mac.

## Add a new template

```bash
# Overlay only (browser source, images)
./scripts/new-template.sh starting-soon "Starting Soon Pack"

# Full scene collection (imports into OBS Scene Collection menu)
./scripts/new-template.sh vibe-coding "Vibe Coding Scene" scene-collection
```

Put files in `templates/<id>/`. For scene collections, export JSON to `scene/` and use `{{INSTALL_DIR}}` for asset paths:

```json
"local_file": "{{INSTALL_DIR}}/overlays/orb.html"
```

Then ship:

```bash
./scripts/ship.sh "Add starting-soon template"
```

## What each zip includes (auto-generated)

| File | Purpose |
|------|---------|
| `install.command` | Mac double-click installer |
| `Install.bat` | Windows double-click installer |
| `install.py` | Copies files + registers scene in OBS |
| `docs/install-guide.html` | Step-by-step slide deck in browser |
| `README.md` | Text install + video link slot |

On Mac, installers copy to `~/Library/Application Support/OBS-Templates/<template-id>/`. Scene JSON lands in OBS's scenes folder.

## Video walkthroughs (recommended)

Auto-generated slides cover most users. For each template, record a **60–90 second** screen capture during stream:

1. Unzip → double-click install → show it in OBS
2. Upload to YouTube (**Unlisted** is fine)
3. Add link in template `README.md` under **Video walkthrough**

Example:

```markdown
## Video walkthrough

[Watch install (1 min)](https://youtu.be/xxxxx)
```

No need for fancy editing — raw OBS or QuickTime is fine.

## Stream link

`https://github.com/TonkaToyXL/obs-templates`
