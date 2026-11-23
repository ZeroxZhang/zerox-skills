#!/usr/bin/env bash
# Install and verify the Python Playwright package and Chromium browser.
#
# The script is idempotent. On systems whose system Python refuses package
# installs (PEP 668 / "externally managed environment", common on Homebrew and
# recent Debian), it falls back to a dedicated virtualenv and reports the
# interpreter to use for capture.py / render_check.py via PLAYWRIGHT_PYTHON.

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

REQUIREMENTS="$(cd "$(dirname "$0")/.." && pwd)/requirements.txt"
PYTHON_BIN="python3"

if python3 -c "import playwright" >/dev/null 2>&1; then
    echo "[1/3] Playwright Python package is already installed for python3."
else
    echo "[1/3] Installing the Playwright Python package..."
    if python3 -m pip install -r "$REQUIREMENTS" >/dev/null 2>&1; then
        echo "      Installed into the system Python."
    else
        VENV_DIR="${ZEROX_ONEPAGER_VENV:-$HOME/.cache/zerox-onepager/venv}"
        echo "      System Python refused the install (PEP 668). Using a virtualenv instead."
        echo "      Virtualenv: $VENV_DIR"
        if [ ! -x "$VENV_DIR/bin/python" ]; then
            python3 -m venv "$VENV_DIR"
        fi
        "$VENV_DIR/bin/python" -m pip install --quiet --upgrade pip
        "$VENV_DIR/bin/python" -m pip install --quiet -r "$REQUIREMENTS"
        PYTHON_BIN="$VENV_DIR/bin/python"
        echo "      Installed into $PYTHON_BIN"
    fi
fi

echo "[2/3] Checking the Chromium browser..."
if "$PYTHON_BIN" - <<'PY'
import os
from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    raise SystemExit(0 if os.path.isfile(playwright.chromium.executable_path) else 1)
PY
then
    echo "      Chromium is already installed."
else
    echo "      Installing Chromium for $PYTHON_BIN ..."
    "$PYTHON_BIN" -m playwright install chromium
fi

echo "[3/3] Verifying..."
"$PYTHON_BIN" - <<'PY'
import os
from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    executable = playwright.chromium.executable_path
    if not os.path.isfile(executable):
        raise SystemExit(f"ERROR: Chromium executable was not found after installation: {executable}")
    print(f"      Verified Chromium: {executable}")
PY

# Chinese glyph coverage matters for every style except G2-on-a-CJK-host.
if [ "$(uname -s)" = "Linux" ] && command -v fc-list >/dev/null 2>&1; then
    if [ -z "$(fc-list :lang=zh 2>/dev/null | head -n 1 || true)" ]; then
        echo "WARNING: no CJK system font detected. Chinese text will render as tofu."
        echo "         Install one, e.g. Debian/Ubuntu: apt-get install -y fonts-noto-cjk"
        echo "         Fedora/RHEL: dnf install -y google-noto-sans-cjk-ttc-fonts"
    else
        echo "      CJK system fonts detected."
    fi
fi

echo "PLAYWRIGHT_PYTHON=$PYTHON_BIN"
if [ "$PYTHON_BIN" != "python3" ]; then
    echo "NOTE: use $PYTHON_BIN for capture.py and render_check.py on this machine."
fi
echo "=== Dependency check complete ==="
