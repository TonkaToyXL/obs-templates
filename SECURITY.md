# Security Policy

## What ships in this repo

Public, free OBS template files only — overlays, assets, and install docs. No accounts, no telemetry, no backend.

## User-local secrets (never commit these)

- OBS WebSocket passwords — set `OBS_WS_PASS` in the bridge environment if you prefer. The bridge can also read OBS's local WebSocket config at runtime when auth is enabled, but it does not log, copy, or commit the password.
- Mic names, stream keys, and scene paths on a user's machine stay on their machine.

## What the installer changes (safe)

| Action | Scope |
|--------|--------|
| Copy template files | **Mac:** `~/Library/Application Support/OBS-Templates/<name>/` · **Windows:** `~/Documents/OBS-Templates/<name>/` |
| Register scene | OBS `basic/scenes/<name>.json` |
| Enable WebSocket | Local only (`127.0.0.1:4455`) — only if disabled; backs up config first |
| Preserve WebSocket auth | Uses the existing local password when OBS requires auth; does not disable auth |
| Start bridge (Mac) | LaunchAgent runs `bridge/start-bridge.sh` at login |

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
