# Instagram Photo Downloader

维护地址 / Maintained at: [zerox-ins-photo-downloader](https://github.com/ZeroxZhang/zerox-skills/tree/main/zerox-ins-photo-downloader) · 调用 / Invoke: `/zerox-ins-photo-downloader`

> Download **ALL** photos from an Instagram profile to your local disk, sorted by publish time.
> 将 Instagram 个人主页上的**全部照片**下载到本地，并按发布时间排序。

---

## 📖 Introduction / 项目简介

**English** — This tool backs up every photo from an Instagram profile into a local folder.
It extracts your Instagram login session from Chrome, scrolls the profile page in a real
browser to collect all post metadata, then downloads the highest-quality version of each
image. Files are named with the publish timestamp as prefix, so **sorting the folder by
filename equals sorting by publish time**.

**中文** — 本项目用于将 Instagram 个人主页上的全部照片备份到本地文件夹。工具会先从
Chrome 中提取你的 Instagram 登录会话，在真实浏览器中滚动加载个人主页以采集全部帖子
的元数据，再下载每张图片的最高质量版本。文件名以发布时间为前缀，因此**按文件名排序
即等于按发布时间排序**。

## ✨ Features / 功能特性

- 📥 Downloads every photo (single posts and every image inside carousels) — 下载全部照片（单图帖与轮播帖中的每张图）
- 🕐 Files prefixed with `YYYYMMDD_HHMMSS` — sorting by name = sorting by publish time — 文件名以发布时间为前缀，按名称排序即按时间排序
- 🖼️ Picks the **largest** available image candidate per post — 每帖自动选择**最大**分辨率图片
- 🎬 Skips videos (`media_type == 2`) — 自动跳过视频
- 🔁 Re-runs safely: existing files are reused, only missing ones are downloaded — 可安全重跑：已存在文件自动跳过
- 🛡️ Extracts cookies locally from Chrome — no manual session copy-paste — 本地从 Chrome 提取 Cookie，无需手动粘贴会话

## 🏗️ Technical Approach / 技术方案

| Component / 组件 | Tech / 技术 | Role / 职责 |
| --- | --- | --- |
| `scripts/extract_cookies.py` | Python 3 · pycryptodome · requests | Decrypt Chrome cookie DB (Keychain key + PBKDF2 + AES-CBC) to obtain the Instagram login session — 解密 Chrome Cookie 数据库（Keychain 密钥 + PBKDF2 + AES-CBC），获取 Instagram 登录会话 |
| `scripts/collect_posts.js` | Node.js ≥ 18 · Playwright (headless Chromium) | Scroll the profile page and intercept `/graphql/query` responses to collect every post's shortcode, publish time and image URLs — 滚动加载主页并拦截 `/graphql/query` 响应，采集每篇帖子的短码、发布时间与图片地址 |
| `scripts/download_photos.py` | Python 3 · requests · pillow | Download the largest candidate of each image, expand carousels, and rename to timestamp-prefixed filenames — 下载每张图片的最大候选、展开轮播、重命名为时间戳前缀文件名 |

**Why a real browser is required / 为什么必须用真实浏览器：** Instagram's lightweight
endpoints are locked down — `web_profile_info` returns empty edges, `feed/user` returns
empty items, and old GraphQL query hashes return HTTP 400. Scrolling a real browser and
intercepting the page's own GraphQL traffic is the only reliable path.
Instagram 的轻量接口均已加锁——`web_profile_info` 返回空边、`feed/user` 返回空列表、
旧版 GraphQL 查询哈希返回 HTTP 400。滚动真实浏览器并拦截页面自身的 GraphQL 流量是唯一
可靠方案。

## 📁 Directory Structure / 目录结构

```
zerox-ins-photo-downloader/
├── SKILL.md                  # Agent skill instructions (agent 技能说明)
├── scripts/
│   ├── extract_cookies.py    # Step 1: extract Instagram cookies from Chrome
│   ├── collect_posts.js      # Step 2: scroll & collect all post metadata
│   └── download_photos.py    # Step 3: download & rename photos by time
└── .gitignore
```

## 🧰 Prerequisites / 环境要求

- **macOS** with **Google Chrome** installed and logged into Instagram (any profile that has visited instagram.com works)
- **Python 3** — install once:
  ```bash
  python3 -m venv .venv && .venv/bin/pip install pycryptodome requests pillow
  ```
- **Node.js ≥ 18** with the `playwright` package resolvable and a cached Playwright Chromium build:
  ```bash
  npx playwright install chromium
  ```

## 🚀 Usage / 使用方法

Run the three scripts in order from the `scripts/` directory. Each script is
self-contained and takes explicit paths via CLI flags.
在 `scripts/` 目录下按顺序运行以下三个脚本，各脚本相互独立，通过命令行参数指定路径。

### Step 1 — Extract cookies / 提取 Cookie

```bash
python extract_cookies.py --domain instagram.com --out cookies.json
```

Expected output: `OK: 6 cookies extracted` plus a `sessionid` line.
If it fails with "no cookies found", log into Instagram in Chrome first and retry.
预期输出 `OK: 6 cookies extracted` 及 `sessionid` 行；若提示 "no cookies found"，请先在
Chrome 中登录 Instagram 后重试。

### Step 2 — Collect all posts / 采集全部帖子

```bash
node collect_posts.js <username> --cookies cookies.json --out posts_meta.json
```

The script prints a running count (e.g. `captured 12 posts, has_next: true`) and finishes
with `FINAL: collected N posts`. **Verify N is positive before downloading.**
脚本会实时打印进度，并以 `FINAL: collected N posts` 结束。**下载前请确认 N > 0。**

Optional flags / 可选参数: `--chromium <path>`, `--max-scrolls <n>` (for very large accounts / 超大账号).

### Step 3 — Download & sort / 下载并排序

```bash
python download_photos.py --meta posts_meta.json --cookies cookies.json --out instagram_photos
```

Output filenames / 输出文件名示例:

```
20140618_214538_pYzdmAqFNU.jpg     <- single photo / 单图
20190502_032203_Bw7nVQVFZwC_2.jpg  <- 2nd image of a carousel / 轮播第 2 张
```

## ✅ Verification / 下载后校验

1. **Count check / 数量校验** — expected images = posts without carousels + sum of carousel children (videos excluded). Compare to files downloaded.
2. **File validity / 文件有效性**:
   ```bash
   file instagram_photos/*.jpg | grep -cv "JPEG image data"   # expect 0 / 期望为 0
   ```
3. **Ordering / 排序校验** — confirm timestamps are non-decreasing when sorted by name.
4. **Spot check / 抽样检查** — open the first, middle and last image to make sure they aren't placeholders.

## 🔒 Security Note / 安全提示

`cookies.json` contains your **Instagram login session** and is highly sensitive.
Delete it after the download finishes. Never share it or commit it to the repository.
`cookies.json` 包含你的 **Instagram 登录会话**，属于高度敏感文件，下载完成后请删除，
切勿分享或提交到仓库。

## ⚠️ Disclaimer / 免责声明

**English** — This project is provided for **personal backup and archival purposes only**.
It is intended for downloading content you own or are otherwise authorized to save (e.g.
your own account, or with the account owner's explicit permission). Please respect:

- Instagram's / Meta's **Terms of Service** and community guidelines;
- the copyright and privacy rights of the content owner;
- local laws and regulations regarding data collection and personal information.

The author is not affiliated with Instagram or Meta Platforms, Inc., and takes no
responsibility for any misuse of this tool or for any consequences arising from
violating third-party terms or applicable laws. Use it at your own risk.

**中文** — 本项目**仅限个人备份与存档用途**。请只下载你本人拥有、或经账号所有者明确
授权保存的内容（如自己的账号，或已获得对方许可）。请务必遵守：

- Instagram / Meta 的**服务条款**与社区准则；
- 内容所有者的版权与隐私权利；
- 当地关于数据收集与个人信息保护的法律法规。

本项目与 Instagram 及 Meta Platforms, Inc. 无任何关联，作者不对工具的滥用行为，或因
违反第三方条款/适用法律而产生的一切后果承担任何责任。请自行评估风险后使用。

## 📄 License / 许可证

MIT License. See `LICENSE` for details. / 详见 `LICENSE` 文件。
