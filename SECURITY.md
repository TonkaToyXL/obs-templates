# Security Policy

## What ships in this repo

Public, free OBS template files only — overlays, assets, and install docs. No accounts, no telemetry, no backend.

## User-local secrets (never commit these)

- OBS WebSocket passwords — set in OBS and in each user's local copy of `orb.html` (`CONFIG.wsPassword`). The repo ships an **empty** password.
- Mic names, stream keys, and scene paths on a user's machine stay on their machine.

## Before you push

Run the safety scan (also runs automatically when packaging):

```bash
./scripts/validate.sh
```

It blocks personal paths (`/Users/...`), emails, cloud-sync paths, hardcoded passwords, and invalid manifests.

## Reporting a vulnerability

Please report security issues privately through [GitHub Security Advisories](https://github.com/TonkaToyXL/obs-templates/security/advisories/new).

Do not open public issues for exploitable vulnerabilities.
