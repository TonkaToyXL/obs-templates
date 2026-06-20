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
