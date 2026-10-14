#!/usr/bin/env python3
"""Extract cookies for a given domain from the local Chrome profile (macOS).

Usage:
    python extract_cookies.py [--domain instagram.com] [--out cookies.json]

Reads Chrome's encrypted cookie DB, derives the AES key from the macOS
Keychain ("Chrome Safe Storage" password + PBKDF2(saltysalt, 1003, 16B)),
and writes a flat JSON map {cookie_name: {value, host, path}}.

Newer Chrome versions prefix every cookie value with a shared 32-byte
header; the real value starts at byte 32. This script strips it.
"""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

CHROME_DIR = Path.home() / "Library/Application Support/Google/Chrome"
COOKIES_DB = CHROME_DIR / "Default" / "Cookies"
KEYCHAIN_SERVICE = "Chrome Safe Storage"
PREFIX_LEN = 32  # shared prefix in new Chrome cookie format


def get_key() -> bytes:
    out = subprocess.run(
        ["security", "find-generic-password", "-w", "-s", KEYCHAIN_SERVICE],
        capture_output=True, text=True, check=True,
    )
    raw = out.stdout.strip().encode()
    return PBKDF2(raw, b"saltysalt", dkLen=16, count=1003)


def decrypt_value(encrypted: bytes, key: bytes) -> bytes:
    if encrypted[:3] != b"v10":
        return b""
    cipher = AES.new(key, AES.MODE_CBC, b" " * 16)
    padded = cipher.decrypt(encrypted[3:])
    pad = padded[-1]
    if not (1 <= pad <= 16):
        return b""
    return padded[:-pad]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default="instagram.com", help="cookie host filter, e.g. instagram.com")
    ap.add_argument("--out", default="cookies.json", help="output json path")
    args = ap.parse_args()

    key = get_key()
    with tempfile.TemporaryDirectory() as tmp:
        db_copy = os.path.join(tmp, "Cookies")
        shutil.copy2(COOKIES_DB, db_copy)
        con = sqlite3.connect(db_copy)
        con.text_factory = bytes
        cur = con.cursor()
        rows = cur.execute(
            "SELECT host_key, name, encrypted_value, path FROM cookies "
            "WHERE host_key LIKE ? ORDER BY host_key, name",
            (f"%{args.domain}",),
        ).fetchall()
        con.close()

    cookies = {}
    for host_key, name, enc, path in rows:
        val = decrypt_value(enc, key)
        if not val:
            continue
        # strip shared 32-byte prefix when present
        if len(val) > PREFIX_LEN and val[:2] == b"~:":
            val = val[PREFIX_LEN:]
        try:
            text = val.decode("utf-8")
        except UnicodeDecodeError:
            continue
        cookies[name.decode()] = {"value": text, "host": host_key.decode(), "path": path.decode()}

    if not cookies:
        print(f"ERROR: no cookies found for domain {args.domain} (is Chrome logged in?)", file=sys.stderr)
        sys.exit(1)

    Path(args.out).write_text(json.dumps(cookies, indent=2, ensure_ascii=False))
    print(f"OK: {len(cookies)} cookies extracted to {args.out}")
    if "sessionid" in cookies:
        print("sessionid:", cookies["sessionid"]["value"][:30] + "...")


if __name__ == "__main__":
    main()
