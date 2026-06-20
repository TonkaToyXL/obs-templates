# Security Policy

## What ships in this repo

Public, free OBS template files only — overlays, assets, and install docs. No accounts, no telemetry, no backend.

## User-local secrets (never commit these)

- OBS WebSocket passwords — the installer **never reads or copies** your password. If OBS already uses WebSocket auth, set `CONFIG.wsPassword` in the template to match.
- Mic names, stream keys, and scene paths on a user's machine stay on their machine.

## What the installer changes (safe)

| Action | Scope |
|--------|--------|
| Copy template files | `~/Documents/OBS-Templates/<name>/` |
| Register scene | OBS `basic/scenes/<name>.json` |
| Enable WebSocket | Local only (`127.0.0.1:4455`) — only if disabled; backs up config first |
| Disable WebSocket auth | **Only** if no password is set yet |

No network access. No telemetry. No stream keys.

## Before you push

Run the safety scan (also runs automatically when packaging):

```bash
./scripts/validate.sh
```

It blocks personal paths (`/Users/...`), emails, cloud-sync paths, hardcoded passwords, and invalid manifests.

## Reporting a vulnerability

Please report security issues privately through [GitHub Security Advisories](https://github.com/TonkaToyXL/obs-templates/security/advisories/new).

Do not open public issues for exploitable vulnerabilities.
