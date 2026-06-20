#!/usr/bin/env bash
# One command: validate → zip → commit → push. Use this on stream.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MSG="${1:-Update OBS templates}"

./scripts/package.sh

git add -A
if git diff --staged --quiet; then
  echo "Nothing new to ship."
  exit 0
fi

export GIT_AUTHOR_NAME="${GIT_AUTHOR_NAME:-TonkaToyXL}"
export GIT_COMMITTER_NAME="${GIT_COMMITTER_NAME:-TonkaToyXL}"
export GIT_AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-83329120+TonkaToyXL@users.noreply.github.com}"
export GIT_COMMITTER_EMAIL="${GIT_COMMITTER_EMAIL:-83329120+TonkaToyXL@users.noreply.github.com}"

git commit -m "$MSG"
git push origin main

echo
echo "Live — share this link:"
echo "  https://github.com/TonkaToyXL/obs-templates"
