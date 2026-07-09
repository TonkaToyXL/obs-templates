# OBS Templates — agent instructions

Public storefront repo. Safety and validate.sh must pass before any publish.

## Verification (run before finishing any task)

```bash
./scripts/sync-shared.sh
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
./scripts/validate.sh
python3 -m pytest -q
```

`validate.sh` requires `rg` (ripgrep). Install if missing: `brew install ripgrep` (macOS) or `apt-get install ripgrep` (CI).
Edit shared bridge/privacy under `templates/_shared/` only — never only one template copy.
Manifest/scene rules live in `scripts/manifest_validate.py` (used by validate.sh and pytest).

## Scope rules

- Never commit personal paths, emails, secrets, or device-specific mic names.
- Templates ship neutral; TonkaToyXL credit belongs in hub README/docs only.
- Do not modify packaged `dist/*.zip` unless the task explicitly rebuilds releases.
- Do not add dependencies beyond pytest for isolated test tasks.
- Prefer small PRs; do not refactor unrelated scripts.

## Jules specific instructions

- Good tasks: CI workflow, manifest validation tests, README accuracy fixes.
- Avoid: rewriting scene JSON, changing overlay HTML/CSS unless explicitly requested.
- If adding tests, extract pure logic from `validate.sh` into `scripts/manifest_validate.py` rather than duplicating rules.
