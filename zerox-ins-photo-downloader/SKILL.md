---
name: zerox-ins-photo-downloader
description: Download ALL photos from an Instagram profile page to local disk, sorted by publish time. Trigger whenever the user shares an Instagram profile URL (instagram.com/<username>/) and asks to download/save/backup the photos or images from that account, mentions wanting an account's pictures saved locally, or asks to scrape an Instagram profile's media. This skill handles cookie extraction from the logged-in Chrome, browser-based scrolling to collect every post, and time-ordered downloading. Use it even if the user only says "download this account's photos" without naming Instagram — if the link is instagram.com it should trigger.
---

# Instagram Photo Downloader

Downloads every photo from an Instagram profile into a local folder, with
filenames prefixed by publish time so that sorting by name equals sorting by
publish time.

## When to use

- User shares an `https://www.instagram.com/<username>/` link and wants the photos.
- User wants to back up / save / download an account's images locally.
- User wants photos ordered by publish date.

## Prerequisites (host machine)

- **macOS** with **Google Chrome** installed and the user **logged into
  Instagram** in Chrome (any profile that has visited instagram.com works;
  the Default profile is tried first).
- Python 3 with `pycryptodome` and `requests` (install once: `python3 -m venv .venv && .venv/bin/pip install pycryptodome requests pillow`).
- Node.js ≥ 18 with the `playwright` package resolvable, and a Playwright
  Chromium build cached (see the collect script's auto-detection; if missing,
  `npx playwright install chromium`).

## Workflow

Run these three scripts in order from the skill's `scripts/` directory.
The scripts are self-contained: each takes explicit paths via CLI flags, so
you can keep intermediate files anywhere (e.g. the user's workspace).

### Step 1 — Extract the login cookies

```bash
python extract_cookies.py --domain instagram.com --out cookies.json
```

This decrypts Chrome's cookie DB (Keychain key + PBKDF2 + AES-CBC) and writes
a flat JSON map. It strips the shared 32-byte prefix that new Chrome versions
add to every cookie value — **do not remove that logic**; without it the
sessionid comes out as garbage and Instagram rejects the session.

Expect output like `OK: 6 cookies extracted` and a `sessionid` line. If it
fails with "no cookies found", the user is not logged in — ask them to log in
and retry. Never ask the user to paste a sessionid; extracting from Chrome is
the whole point.

### Step 2 — Collect all post metadata by scrolling

```bash
node collect_posts.js <username> --cookies cookies.json --out posts_meta.json
```

The script launches headless Chromium with the extracted cookies, opens the
profile page, scrolls to the bottom repeatedly, and intercepts the
`/graphql/query` POST responses carrying
`xdt_api__v1__feed__user_timeline_graphql_connection`. Each edge's node has
everything needed: `code` (shortcode), `taken_at` (unix seconds), and
`image_versions2.candidates` (image URLs) or `carousel_media` (multi-image
posts). The script dedupes by shortcode and stops when `has_next_page` is
false and the page height stops growing.

**Why the browser approach is required:** Instagram's lightweight API
endpoints are locked down — `web_profile_info` returns only the post count
with empty edges, `feed/user` returns empty items, and the old GraphQL query
hashes return HTTP 400. Scrolling a real browser is the reliable path. Do not
waste time trying the blocked endpoints.

The script prints a running count (e.g. `captured 12 posts, has_next: true`)
and finishes with `FINAL: collected N posts`. **Verify N is positive** before
downloading.

Optional flags: `--chromium <path>` to point at a specific browser binary,
`--max-scrolls <n>` for very large accounts.

### Step 3 — Download and sort by publish time

```bash
python download_photos.py --meta posts_meta.json --cookies cookies.json --out instagram_photos
```

For each post it picks the **largest** image candidate, expands carousels into
individual files, skips videos (`media_type == 2`), and names files:

```
20140618_214538_pYzdmAqFNU.jpg     <- single photo
20190502_032203_Bw7nVQVFZwC_2.jpg  <- 2nd image of a carousel
```

Because the filename begins with `YYYYMMDD_HHMMSS`, **sorting the folder by
filename sorts by publish time** (verified ascending). The script reuses files
that already exist, so re-running is safe.

## Verification (always do this)

After Step 3 completes, verify before reporting success:

1. **Count check** — expected images = posts without carousels + sum of
   carousel children (videos excluded). Compare to files downloaded. If the
   profile said 72 posts and you have 82 jpgs with 6 carousels, that's right.
2. **File validity** — confirm every file is a real image:
   ```bash
   file instagram_photos/*.jpg | grep -cv "JPEG image data"   # expect 0
   ```
3. **Ordering** — confirm timestamps are non-decreasing when sorted by name.
4. **Spot check** — open the first, middle, and last image to make sure they
   aren't placeholders or error pages.

## Troubleshooting

- **"no cookies found"** — user isn't logged into Instagram in Chrome.
- **FINAL collected 0 posts** — session expired or Instagram served a
  challenge/login wall; re-extract cookies (Step 1) and retry. If the account
  is private, only followers can see posts.
- **Playwright can't find a browser** — the script auto-detects
  `~/Library/Caches/ms-playwright/chromium-*`; if none, run
  `npx playwright install chromium`.
- **Some downloads fail (FAIL lines)** — CDN links can 404 if stale; re-run
  the download script; existing files are skipped, only missing ones retry.
- **macOS permission prompts** — the Keychain read may pop a dialog the first
  time; the user should click "Allow".

## Security note

The extracted `cookies.json` contains the user's login session. It is
sensitive — tell the user they may delete it after the download finishes.
Never share it, and don't write it into chat output.
