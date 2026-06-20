# Stream cheat sheet

**Link for YouTube chat / description:**

`https://github.com/TonkaToyXL/obs-templates`

---

## New template (once per pack)

```bash
cd ~/Projects/00_ACTIVE/github-public-publish/obs-templates
./scripts/new-template.sh my-pack-name "My Pack Display Name"
# drop files into templates/my-pack-name/
```

## Ship to GitHub (run after each template is ready)

```bash
./scripts/ship.sh "Add my-pack-name template"
```

That's it. Viewers refresh the README and click Download.

---

## On-stream checklist

1. Build template in OBS
2. Copy files into `templates/<id>/` (not raw OBS config paths — run validate if unsure)
3. Edit `manifest.json` description + folder `README.md` install steps
4. `./scripts/ship.sh "Add <name>"`
5. Paste GitHub link in chat

## If validate fails

It caught a personal path or secret. Fix the file it points at, then ship again.

## Bump an existing template

Edit `version` in `manifest.json` → `./scripts/ship.sh "Update <name> v1.1.0"`
