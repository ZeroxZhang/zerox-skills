# Changelog

All notable changes to the Onepager skill are documented in this file.

## [1.6.0] - 2026-11-23

### Added
- **Composition checker** `scripts/layout_check.py`: measures the rendered page for gaps that break the rhythm (holes), blocks whose content fills under 55% of their own box (content packed at the top), total air ratio against a per-density target, distinct font-size count and max:min scale, and horizontal ink imbalance. Full-bleed colour blocks count as ink, not air. This is the check that catches "looks fine locally, reads as empty space" — the failure mode that static and geometry checks both pass.
- **`references/layout-archetypes.md`**: five poster archetypes with exact row budgets for A4 (band stack, oversized type + side rail, editorial two-column, card matrix, colour-block rhythm), each stating *why* it fills the canvas by construction, plus the three failure signatures it prevents
- **Layout contract in `config-schema.json`**: per-density air-ratio targets (C1 34-52% / C2 22-38% / C3 12-28%), gap-ratio caps, max type scale 12:1 (hard 15:1), max 6 distinct font sizes, max 5% ink imbalance
- **B10 colour roles**: red and cyan are now defined by *function*, not just area — red is the action colour, cyan is the structural colour and must carry at least two structural jobs per page. Combined budget raised from 12% to 12-16%, because squeezing cyan under 4% turns B10 into a generic dark template with one red button
- **Usage scenes (S1-S6)** as the first decision in the interaction protocol: 产品介绍 / 工作汇报 / 客户沟通 / 活动宣传 / 数据洞察 / 知识方法. Each scene ships a validated default `A/B/C/T/E` configuration, must-have modules, anti-patterns, and an acceptance test; see `references/scenes.md`
- **B10 短视频潮流 (Short-Video Feed)** design style with `Dark` (default) and `Paper` sub-modes, full palette with same-hue scales, six signature devices (chromatic offset, bottom scrim, action rail, mono metadata, hard rules, pill CTA), BigNumber and signature specs, and an explicit boundary against B8
- **Font matching step (Phase 3.7)** and the `G1-G7` font-scheme dimension: automatic matching, system-native, editorial serif, display sans, geometric-tech, handwritten, and custom
- **`references/font-library.md`**: curated open-source / Google Fonts catalog with copy-paste CSS2 URLs, the five-step matching flow, CDN loading rules (`display=swap`, preconnect, `@import`), CJK subsetting notes, per-style mapping for B1-B10, and a forbidden-usage list
- **Design-impact layer** in the visual standards: single hero moment, full-bleed, cropped type, rhythm over equal division, negative space as a subject, optical alignment, and controlled texture
- **Typography contract in the IR**: optional `typography` block (display / body / mono / origin / weights / fallback_chain / cdn_url) plus `S`, `G`, `B_mode`, `G_font` in `configuration`

### Changed
- The type rule is now a band, not a floor: 8:1 to 12:1 with at most six distinct sizes. The old "at least 10:1" wording pushed generated pages into 150px headlines beside 11px body text
- Poster composition starts from a named archetype instead of an invented grid; `justify-content: space-between` over percentage bands is called out as the direct cause of band voids
- The interaction protocol is now `S/A/B/C/T/E/G/F`. `S` is asked first and presets the rest; the original `A/B/C/T/E/F` dimensions are all retained and remain user-overridable
- The `D` menu label was corrected to `T` to match its `T1-T4` codes
- `quality_check.py` gained `[FONT]` checks (generic fallback, `display=swap`, loaded-but-unused families, family count, CJK coverage), a `[TYPO]` type-scale check that tightens to 8:1 and ERROR for `--type T4`, a new `--type` flag, and contrast detection for `.poster` / `.canvas` page roots
- Single-hue alpha-ramp gradients (`to top`) are now recognised as readability scrims instead of being reported as unexplained decoration
- `project.py` accepts optional `--S` and `--G` and validates them against the schema; the recorded tool version is now `1.6.0`
- `base-skeleton.html` now ships preconnect + `display=swap` font loading, full-bleed utilities, and B10 chromatic-offset / bottom-scrim shortcuts

### Fixed
- Web-font families declared through CSS variables are no longer reported as "loaded but unused", and CJK stacks declared the same way are now detected correctly
- `examples/b10-poster.example.html` demonstrates a passing `S4 · A4 · B10 · C1 · T4 · E2 · G4` poster — 21/21 checks, zero warnings — with its render at `examples/b10-poster.example.png`

## [1.5.0] - 2026-08-08

### Added
- Machine-readable configuration source of truth at `references/config-schema.json`
- Content Blueprint, Onepager IR, and reproducible Manifest schemas
- `scripts/project.py` for project initialization, versioning, verified build recording, and hash validation
- Example Blueprint and IR assets plus an executable product development backlog
- Browser-backed `render_check.py` for canvas dimensions, clipping, overflow, boundaries, page errors, and failed resources
- Unit and Playwright integration tests with GitHub Actions CI
- Runtime dependency manifest and idempotent Playwright/Chromium installation

### Changed
- The complete `A/B/C/T/E/F` menu is explicitly retained as the core user interaction protocol; recommendations explain choices but never silently replace user confirmation
- Phase 1 now produces a user-visible content blueprint before the configuration interaction
- Confirmed configuration and stable content-module IDs are persisted in Onepager IR
- Content reconstruction no longer invents metrics, cases, credentials, or missing factual details
- Missing verified BigNumber data now falls back to E2 unless the user explicitly requests a labeled scenario assumption
- B9/T4 mode and A2/A3/A4 fixed-height rules are consistent across the primary instructions and references
- `quality_check.py` now validates each CSS rule, resolves CSS variables, parses inline styles, and distinguishes hard errors from advisory warnings
- `capture.py` now fails closed on navigation/font/page errors, writes atomically, validates arguments, and verifies final PNG dimensions
- Network fonts are optional enhancements with required system fallbacks rather than a self-contained-file guarantee

### Fixed
- Non-B9 palettes with seven or fewer colors can now pass
- Semantic footers, exact BigNumber classes, CSS absolute positioning, per-grid rows, inline colors, spaced RGB syntax, and CSS-variable contrast are handled correctly
- Copyright and other non-emoji symbols no longer trigger the Emoji rule
- Playwright installation no longer skips a missing Chromium browser
- Removed the obsolete T6 showcase and tracked `.DS_Store`
- Replaced the missing poster-reference filename with the maintained B9/T4 showcase

## [1.4.0] - 2026-05-29

### Added
- **B9 Google Native style**: Complete design specification with Light (Classic Four-Color) and Dark (I/O) dual palette, card styles, heading styles, color budget mapping, icon style, BigNumber CSS, and signature styling
- **B9 typography mapping**: Inter + Noto Sans SC font stack, Chinese-specific weight rules, letter-spacing guidelines, Google Fonts loading
- **B9 diagram color palette**: Brand four-color data series for both Light and Dark modes
- **B9 visual standards**: Icon style and BigNumber differentiation table entries
- **A4 size typography table**: Complete font size ladder for 1080×1440px poster size
- **A4 BigNumber size specs**: Minimum, recommended, unit, and label sizes
- **A4 visual flow direction**: Z-pattern recommendation in visual-standards.md
- **Quote block and Key Insight block**: E2 (no BigNumber) alternative HTML templates in base-skeleton.html
- **12 additional SVG icons**: search, link, mail, calendar, clock, star, download, home, shield, lightbulb, play, code
- **Page size adaptation classes**: `.page-a1` / `.page-a2` / `.page-a3` / `.page-a4` CSS classes in template
- **B9 color block utility classes**: `.color-block-blue` / `.color-block-red` / `.color-block-yellow` / `.color-block-green` in template
- **CHANGELOG.md**: This file

### Changed
- **SKILL.md phase numbering**: Renumbered from 1/2/3/4/4.5/5 to 1/2/3/4/5/6 for clarity
- **Quality check deduplication**: Removed duplicate `quality_check.py` execution; now only runs once in Phase 5 (was Phase 4.5 + Phase 5.2)
- **File naming format**: Date format explicitly specified as `YYYYMMDD`; iteration version appended after date (`{topic}-{size}-{style}-{YYYYMMDD}[-vN].html`)
- **quality_check.py major improvements**:
  - `--size` parameter now actually used: A2/A3/A4 trigger stricter fixed-height layout checks (flex:1 becomes ERROR, missing grid-template-rows becomes WARNING)
  - Color deduplication: colors normalized to RGB tuples before counting, eliminating false duplicates from different color syntaxes
  - Emoji detection: uses `unicodedata.category()` for broader coverage (Emoji Keycap, skin tone modifiers, Supplemental Symbols Extended-A, etc.)
  - Removed redundant flex:1 detection code
  - Multi-element contrast checking: now checks Body text, BigNumber, and Footer independently
  - Removed emoji from terminal output (uses `[X]`/`[!]`/`[OK]` instead of emoji)
  - Removed `#2563eb` from `known_ai_colors` to avoid false positives with B5 (宝蓝)
- **capture.py improvements**:
  - Explicit timeout parameter (`--timeout`, default 30000ms)
  - Graceful timeout handling with warning instead of crash
  - Uses `document.fonts.ready` for font loading detection instead of fixed 2000ms wait
  - Reduced post-render buffer from 2000ms to 500ms
  - Added brief re-render wait after viewport resize for fixed-size screenshots
- **base-skeleton.html**: Removed default decorative `.page::before` blob (was contradicting anti-AI-taste rules)
- **layout-specs.md**: Title updated from "三种尺寸" to "四种尺寸"
- **design-styles.md**: Title updated from "八种" to "九种"; color budget exception text updated to include B9
- **guideline.md**: Repositioned as "design theory reference" rather than operational guide; removed outdated 4-step prompt template
- **README.md**: Fixed size counts (3→4 sizes); fixed layout-specs.md description in file structure
- **visual-standards.md**: Added A4 visual flow direction; updated icon style and BigNumber tables with B9 rows

### Fixed
- `quality_check.py`: Blue-purple detection no longer flags `#2563eb` alone (was in `known_ai_colors` with comment "only flag when paired with purple" but flagged unconditionally)
- `quality_check.py`: `flex:1` inline style check had redundant condition (`s` was already `style.replace(" ", "")`)
