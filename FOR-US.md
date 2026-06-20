# For us — publishing templates

## Safety first (every time)

```bash
./scripts/validate.sh    # blocks personal paths, emails, secrets, bad manifests
./scripts/package.sh     # validate runs automatically, then builds zips
```

**Never commit:**

- Your OBS scene JSON straight from `~/Library/Application Support/obs-studio/` — it contains `/Users/you/...` paths
- WebSocket passwords, stream keys, API tokens
- Personal logos unless they're already public brand assets
- Mic names like `BLUE NESSIE USB MIC` in shared defaults — leave `micInputName` blank in shipped HTML

**Before exporting a scene collection:** search/replace absolute paths with relative paths inside the template folder, or run validate and fix anything it flags.

## Add a new template

```bash
./scripts/new-template.sh starting-soon "Starting Soon Pack"
# add files under templates/starting-soon/
./scripts/package.sh starting-soon
git add . && git commit -m "Add starting-soon v1.0.0" && git push
```

Folders starting with `_` are ignored by packaging (use for scratch/drafts).

## Bump a version

1. Edit `version` in `templates/<id>/manifest.json` (semver: `1.0.1`)
2. `./scripts/package.sh <id>`
3. Commit and push

Old zips in `dist/` can be deleted when version bumps — README only links current builds.

## First-time GitHub setup

```bash
gh repo create TonkaToyXL/obs-templates --public --source=. --remote=origin --push
```

Use the TonkaToyXL GitHub noreply commit email (same as other public repos).

## Stream link

`https://github.com/TonkaToyXL/obs-templates`
