#!/usr/bin/env bash
# Install and verify the Python Playwright package and Chromium browser.

set -euo pipefail

echo "=== zerox-onepager: checking screenshot dependencies ==="

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: Python 3 is required but not found." >&2
    exit 1
fi

python3 - <<'PY'
import sys

if sys.version_info < (3, 8):
    raise SystemExit(f"ERROR: Python 3.8+ is required. Current version: {sys.version}")
PY

if ! python3 -c "import playwright" >/dev/null 2>&1; then
    echo "[1/2] Installing the Playwright Python package..."
    python3 -m pip install -r "$(dirname "$0")/../requirements.txt"
else
    echo "[1/2] Playwright Python package is already installed."
fi

if python3 - <<'PY'
import os
from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    raise SystemExit(0 if os.path.isfile(playwright.chromium.executable_path) else 1)
PY
then
    echo "[2/2] Chromium is already installed."
else
    echo "[2/2] Installing Chromium for the active Python environment..."
    python3 -m playwright install chromium
fi

python3 - <<'PY'
import os
from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    executable = playwright.chromium.executable_path
    if not os.path.isfile(executable):
        raise SystemExit(f"ERROR: Chromium executable was not found after installation: {executable}")
    print(f"Verified Chromium: {executable}")
PY

echo "=== Dependency check complete ==="
