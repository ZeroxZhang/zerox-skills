#!/usr/bin/env node
/**
 * Collect all post metadata from an Instagram profile by scrolling.
 *
 * Usage:
 *   node collect_posts.js <username> [--cookies cookies.json] [--out posts_meta.json]
 *                          [--chromium <path>] [--max-scrolls 60]
 *
 * Strategy (validated against modern Instagram):
 *   - Traditional endpoints are blocked: web_profile_info returns only the post
 *     count with empty edges; feed/user and old GraphQL query hashes return
 *     empty/400. The ONLY reliable path is driving a real browser with the
 *     user's logged-in cookies and scrolling the profile page.
 *   - Scrolling triggers POST /graphql/query responses containing
 *     xdt_api__v1__feed__user_timeline_graphql_connection with edges
 *     (node.code, node.taken_at unix seconds, node.image_versions2.candidates,
 *     node.carousel_media[]) and page_info.end_cursor / has_next_page.
 *   - We intercept those responses, dedupe by post code, and keep scrolling
 *     until has_next_page is false and the page height stops growing.
 *
 * Output: JSON array of graphql edges (full nodes) written to --out.
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

function findChromium() {
  if (process.env.PLAYWRIGHT_CHROMIUM) return process.env.PLAYWRIGHT_CHROMIUM;
  const cache = path.join(process.env.HOME, 'Library/Caches/ms-playwright');
  try {
    const dirs = fs.readdirSync(cache)
      .filter(d => d.startsWith('chromium-') && !d.includes('headless'))
      .sort();
    for (const d of dirs.reverse()) {
      const cand = path.join(cache, d, 'chrome-mac-arm64', 'Google Chrome for Testing.app', 'Contents/MacOS', 'Google Chrome for Testing');
      const candIntel = path.join(cache, d, 'chrome-mac', 'Google Chrome for Testing.app', 'Contents/MacOS', 'Google Chrome for Testing');
      for (const c of [cand, candIntel]) {
        if (fs.existsSync(c)) return c;
      }
    }
  } catch (e) { /* no cache */ }
  return undefined; // let playwright use its default
}

function parseArgs() {
  const argv = process.argv.slice(2);
  const args = { username: null, cookies: 'cookies.json', out: 'posts_meta.json', chromium: undefined, maxScrolls: 60 };
  for (let i = 0; i < argv.length; i++) {
    switch (argv[i]) {
      case '--cookies': args.cookies = argv[++i]; break;
      case '--out': args.out = argv[++i]; break;
      case '--chromium': args.chromium = argv[++i]; break;
      case '--max-scrolls': args.maxScrolls = parseInt(argv[++i], 10) || 60; break;
      default:
        if (!args.username) args.username = argv[i];
    }
  }
  return args;
}

(async () => {
  const args = parseArgs();
  if (!args.username) {
    console.error('Usage: node collect_posts.js <username> [--cookies cookies.json] [--out posts_meta.json]');
    process.exit(1);
  }
  if (!fs.existsSync(args.cookies)) {
    console.error(`cookies file not found: ${args.cookies} (run extract_cookies.py first)`);
    process.exit(1);
  }

  const cookies = JSON.parse(fs.readFileSync(args.cookies, 'utf8'));
  const exec = args.chromium || findChromium();
  const browser = await chromium.launch(exec ? { executablePath: exec, headless: true } : { headless: true });
  const ctx = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 900 },
    locale: 'zh-CN',
  });
  await ctx.addCookies(Object.entries(cookies).map(([name, c]) => ({ name, value: c.value, domain: c.host, path: c.path })));
  const page = await ctx.newPage();

  const allEdges = [];
  const seen = new Set();
  let pageInfo = null;

  page.on('response', async (resp) => {
    const u = resp.url();
    if (u.includes('/graphql/query') && resp.request().method() === 'POST') {
      try {
        const j = await resp.json();
        const conn = j?.data?.xdt_api__v1__feed__user_timeline_graphql_connection;
        if (conn && Array.isArray(conn.edges)) {
          pageInfo = conn.page_info;
          for (const e of conn.edges) {
            const code = e?.node?.code;
            if (code && !seen.has(code)) {
              seen.add(code);
              allEdges.push(e);
            }
          }
          console.log(`captured ${allEdges.length} posts, has_next: ${pageInfo?.has_next_page}`);
        }
      } catch (e) { /* non-json */ }
    }
  });

  await page.goto(`https://www.instagram.com/${args.username}/`, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.waitForTimeout(5000);

  let stableScrolls = 0;
  for (let i = 0; i < args.maxScrolls; i++) {
    const h = await page.evaluate(() => document.body.scrollHeight);
    await page.mouse.wheel(0, 2500);
    await page.waitForTimeout(1200);
    const h2 = await page.evaluate(() => document.body.scrollHeight);
    if (h2 === h && !pageInfo?.has_next_page) {
      stableScrolls++;
      if (stableScrolls >= 3) break;
    } else {
      stableScrolls = 0;
    }
  }
  await page.waitForTimeout(3000);

  console.log('FINAL: collected', allEdges.length, 'posts');
  fs.writeFileSync(args.out, JSON.stringify(allEdges, null, 1));
  console.log('saved to', args.out);
  await browser.close();
})().catch(e => { console.error('ERR:', e.message); process.exit(1); });
