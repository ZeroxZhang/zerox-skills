#!/usr/bin/env python3
"""Download all photos from collected Instagram post metadata.

Usage:
    python download_photos.py [--meta posts_meta.json] [--cookies cookies.json]
                              [--out instagram_photos]

Extracts every image URL from the post nodes (single posts use
node.image_versions2; carousels use node.carousel_media[] children; videos
media_type==2 are skipped), picks the largest candidate per image, then
downloads with filenames prefixed by publish time:

    YYYYMMDD_HHMMSS_<shortcode>.jpg        (single image)
    YYYYMMDD_HHMMSS_<shortcode>_2.jpg      (2nd image of a carousel)

Filename ordering therefore equals publish-time ordering, oldest first.
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import requests


def best_candidate(image_versions2):
    cands = (image_versions2 or {}).get("candidates") or []
    if not cands:
        return None
    return max(cands, key=lambda c: (c.get("width", 0) or 0) * (c.get("height", 0) or 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", default="posts_meta.json")
    ap.add_argument("--cookies", default="cookies.json")
    ap.add_argument("--out", default="instagram_photos")
    args = ap.parse_args()

    posts = json.loads(Path(args.meta).read_text())
    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True)

    cookies = json.loads(Path(args.cookies).read_text())
    jar = requests.cookies.RequestsCookieJar()
    for name, c in cookies.items():
        jar.set(name, c["value"], domain=c["host"], path=c["path"])

    s = requests.Session()
    s.cookies = jar
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": "https://www.instagram.com/",
    })

    # (taken_at, shortcode, index, url) for every image
    items = []
    for p in posts:
        n = p.get("node", p)
        taken = n.get("taken_at")
        code = n.get("code", "unknown")
        carousel = n.get("carousel_media") or []
        if carousel:
            for i, m in enumerate(carousel):
                if m.get("media_type") == 2:
                    continue  # skip video children
                cand = best_candidate(m.get("image_versions2"))
                if cand:
                    items.append((taken, code, i, cand["url"]))
        else:
            cand = best_candidate(n.get("image_versions2"))
            if cand:
                items.append((taken, code, 0, cand["url"]))

    items.sort(key=lambda x: (x[0] or 0, x[1], x[2]))
    print(f"total images to download: {len(items)}")

    ok, failed = 0, []
    for taken, code, idx, url in items:
        dt = datetime.fromtimestamp(taken, tz=timezone.utc).astimezone() if taken else None
        ts = dt.strftime("%Y%m%d_%H%M%S") if dt else "unknown_time"
        suffix = f"_{idx + 1}" if idx > 0 else ""
        fname = f"{ts}_{code}{suffix}.jpg"
        fpath = out_dir / fname

        if fpath.exists() and fpath.stat().st_size > 0:
            ok += 1
            continue
        try:
            r = s.get(url, timeout=60)
            r.raise_for_status()
            fpath.write_bytes(r.content)
            ok += 1
            print(f"  OK {fname} ({len(r.content) // 1024} KB)")
        except Exception as e:
            failed.append((fname, str(e)))
            print(f"  FAIL {fname}: {e}")

    print(f"\nDone. Downloaded {ok} files to {out_dir}")
    if failed:
        print(f"{len(failed)} failed:")
        for f, e in failed:
            print("  ", f, e)


if __name__ == "__main__":
    main()
