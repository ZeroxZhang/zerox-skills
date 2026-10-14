/* 布局图谱防漂移：assets/layout-atlas.html 必须是 references/layouts.md 的可视图，
   舞台几何、页级类名与排印 token 必须与成稿逐字一致。
   默认只跑静态部分（不依赖浏览器）；加 --browser 再用 Playwright 实测区边界、
   区数、行模板与高度容量——"图谱就是 regions 的可视图"要靠断言保证，不靠人眼。 */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path');
const forms = require('../assets/deck-forms.js');
const typography = require('../assets/deck-typography.js');
const C = require('./check_pages.cjs');

const ROOT = path.join(__dirname, '..');
const read = file => fs.readFileSync(path.join(ROOT, file), 'utf8');
const md = read('references/layouts.md');
const atlas = read('assets/layout-atlas.html');
const layoutsCSS = read('assets/consulting-layouts.css');
const engine = read('assets/deck_engine.html');
const results = {};
const PRESET = 'serif-report-bold';

/* ——— 文档侧：按 layouts.md 的固定字段切条目，切法与图谱构建口径一致 ——— */
function docEntries() {
  const out = [];
  let family = null, cur = null;
  for (const line of md.split('\n')) {
    const h3 = line.match(/^### ([甲乙丙丁戊己庚辛] .+)$/);
    if (h3) family = h3[1];
    if (line.startsWith('## 结构页')) family = '结构页';
    const h4 = line.match(/^#### (\S+) (.+)$/);
    if (h4) { cur = {id: h4[1], name: h4[2].trim(), family, raw: {}}; out.push(cur); continue; }
    if (!cur) continue;
    const field = line.match(/^- \*\*(读者任务|阅读路径|落地|regions|取舍|不该用|常见 form)\*\*：(.*)$/);
    if (field) cur.raw[field[1]] = field[2];
  }
  for (const e of out) {
    e.use = e.raw['读者任务'] || '';
    e.path = e.raw['阅读路径'] || '';
    e.land = e.raw['落地'] || '';
    e.trade = e.raw['取舍'] || '';
    e.avoid = e.raw['不该用'] || '';
    const json = (e.raw['regions'] || '').match(/`(\[[\s\S]*?\])`/);
    e.regions = json ? JSON.parse(json[1]) : null;
    const names = (e.raw['常见 form'] || '').match(/`((?:kit|recipe|precision|diagram|html)\.[a-zA-Z]+|svg\.custom)`(†?)/g) || [];
    e.forms = names.map(s => { const m = s.match(/`([^`]+)`(†?)/); return {name: m[1], dagger: m[2] === '†'}; });
  }
  return out;
}
const DOC = docEntries();
const CAT = JSON.parse(atlas.match(/<script type="application\/json" id="layout-catalog">([\s\S]*?)<\/script>/)[1]);

/* 1. 图谱必须是文档的可视图：条目、顺序、正文与 regions 全部逐字对得上。
   只比 id 集合不够——那样改了读者任务或 span，图谱会在无人察觉时变成另一份数据。 */
{
  assert.equal(DOC.length, 27, 'layouts.md 条目数变了：' + DOC.length);
  assert.deepEqual(CAT.map(e => e.id), DOC.map(e => e.id), '图谱条目与文档不一致（缺项或顺序不同）');
  assert.deepEqual(CAT.map(e => e.family), DOC.map(e => e.family), '图谱族名与文档不一致');
  DOC.forEach((d, i) => {
    const a = CAT[i];
    const at = '图谱 ' + a.id + '：';
    assert.equal(a.name, d.name, at + '名称与文档不一致');
    assert.equal(a.use, d.use, at + '读者任务与文档不一致');
    assert.equal(a.path, d.path, at + '阅读路径与文档不一致');
    assert.equal(a.trade, d.trade, at + '取舍与文档不一致');
    assert.equal(a.avoid, d.avoid, at + '「不该用」与文档不一致');
    assert.deepEqual(a.regions, d.regions, at + 'regions 与文档不一致');
    assert.deepEqual(a.forms, d.forms, at + '常见 form 与文档不一致（含 † 标记）');
    assert.ok(d.regions && d.regions.length, at + '文档缺少可解析的 regions');
  });
  results.view_of_doc = CAT.length;
}

/* 2. 反引号里的页级类名必须真实存在：文档不能引用一个没人写过的类。 */
{
  const declared = new Set((layoutsCSS + read('assets/deck-geometry.css')).match(/\.[a-zA-Z][\w-]*/g) || []);
  const unknown = new Set();
  for (const m of md.matchAll(/`\.([a-zA-Z][\w-]*)`/g)) if (!declared.has('.' + m[1])) unknown.add(m[1]);
  assert.deepEqual([...unknown], [], 'layouts.md 引用了不存在的类名');
  results.classes_ok = true;
}

/* 3. 每条 form 都能被实现入口认出来；† 必须与通用标注层接入状态一一对应。
   † 只是文档记号，写错会让人以为可以声明 annotations，check_pages 会当场拒绝。 */
{
  const seen = new Set();
  for (const e of DOC.concat(CAT)) {
    for (const f of e.forms) {
      assert.doesNotThrow(() => forms.get(f.name), e.id + ' 的 ' + f.name + ' 不存在于 deck-forms.js');
      seen.add(f.name);
      assert.equal(f.dagger, forms.get(f.name).annotation === 'layer',
        e.id + ' 的 ' + f.name + '：† 标记与 annotation 不一致');
    }
  }
  results.forms_ok = seen.size;
}

/* 4. 文档里的 regions 直接过真正的 pages 校验器，不另写一套规则。
   regions 里的 `"<本页 form>"` 是占位，按该条目建议的第一个 form 解析——与图谱 resolveForm 同一条规则。 */
{
  let checked = 0;
  /* 首形式是 svg.custom 的条目，合成的页面要补 encodingFamily：契约要求未登记入口自报实际编码族，
     否则这一族在分布记账里是隐形的。丙-3 是同尺度小多图——多个序列共用一把量尺，编码族是 trend。 */
  const ENCODING_BY_LAYOUT = {'丙-3': 'trend'};
  const unresolved = DOC.filter(d => d.forms.length && d.forms[0].name === 'svg.custom' && !ENCODING_BY_LAYOUT[d.id]).map(d => d.id);
  assert.deepEqual(unresolved, [], '这些条目的首形式是 svg.custom，却没有登记实际编码族：' + unresolved.join('、'));
  for (const d of DOC) {
    const regions = d.regions.map(r => (r.form === '<本页 form>' && d.forms.length ? {...r, form: d.forms[0].name} : r));
    const primary = regions.find(r => r.role === 'primary');
    assert.ok(primary, d.id + '：regions 缺少 primary');
    const encoding = primary.form === 'svg.custom' ? {encodingFamily: ENCODING_BY_LAYOUT[d.id]} : {};
    const doc = {version: 1, pages: [{page: 1, proves: d.use || '示例', form: primary.form, visual: primary.visual, ...encoding, regions}]};
    const res = C.check(doc);
    assert.equal(res.status, 'PASS', d.id + ' 的 regions 没过 pages 校验：' + res.errors.join('；'));
    checked += regions.length;
  }
  results.regions_checked = checked;
}

/* 5. 图谱自包含：离线双击就能开。除同目录字体外不得有任何外部引用。 */
{
  const stripped = atlas.replace(/\/\*[\s\S]*?\*\//g, '').replace(/<!--[\s\S]*?-->/g, '');
  assert.ok(!/<script[^>]+\bsrc=/i.test(stripped), '图谱不得引用外部脚本');
  assert.ok(!/@import/i.test(stripped), '图谱不得 @import');
  assert.ok(!/https?:\/\//i.test(stripped), '图谱不得含外部 URL');
  const refs = [...stripped.matchAll(/\b(?:href|src)="([^"]+)"/g)].map(m => m[1]);
  assert.deepEqual(refs, ['fonts/deck-fonts.css'],
    '图谱唯一允许的外部引用是 fonts/deck-fonts.css，实际：' + (refs.join(' ') || '（无）'));
  results.self_contained = refs.length;
}

/* 6. class 结构的 grid/gap 必须与 consulting-layouts.css 的同名规则逐字一致。
   图谱不能加载那份 CSS（会把组件样式带进来），所以它是副本——这里把副本变成可检测副本。 */
{
  const propOf = (cls, prop) => {
    const rule = layoutsCSS.match(new RegExp('\\.' + cls + '\\{([^}]*)\\}'));
    assert.ok(rule, '找不到 .' + cls + ' 的规则');
    const hit = rule[1].match(new RegExp('(?:^|;)' + prop + ':([^;]+)'));
    assert.ok(hit, '.' + cls + ' 没有声明 ' + prop);
    return hit[1].trim();
  };
  let classes = 0;
  for (const e of CAT) {
    if (e.build.kind !== 'class') continue;
    const axis = e.build.axis === 'rows' ? 'grid-template-rows' : 'grid-template-columns';
    assert.equal(e.build.grid, propOf(e.build.cls, axis), e.id + '：图谱 grid 与 .' + e.build.cls + ' 的 ' + axis + ' 不一致');
    assert.equal(e.build.gap + 'px', propOf(e.build.cls, 'gap'), e.id + '：图谱 gap 与 .' + e.build.cls + ' 不一致');
    classes++;
  }
  // 反向：这 5 个页级类必须都被图谱用上，否则图谱漏收了结构
  const used = new Set(CAT.filter(e => e.build.kind === 'class').map(e => e.build.cls));
  for (const cls of ['layout-split', 'layout-three', 'layout-paired', 'layout-stack', 'evidence-grid'])
    assert.ok(used.has(cls), '图谱没有覆盖 .' + cls);
  results.class_geometry = classes;
}

/* 7. 画布与排印常量：图谱声明的 1280×720 / 32·40·26 / 1200×662 必须等于引擎与
   .slide.reading 的实际值；角色字号行高必须等于 deck-typography.js 的预设。 */
{
  const gSrc = atlas.match(/const G = \{([\s\S]*?)\};/)[1];
  const G = {};
  for (const m of gSrc.matchAll(/(\w+):\s*([\d.]+)\s*(?=[,\n])/g)) G[m[1]] = Number(m[2]);
  for (const key of ['W', 'H', 'padT', 'padX', 'padB', 'contentW', 'contentH'])
    assert.ok(Number.isFinite(G[key]), '图谱 G 缺少 ' + key);
  const engineW = engine.match(/--slide-w:(\d+px)/), engineH = engine.match(/--slide-h:(\d+px)/);
  assert.equal(G.W + 'px', engineW[1], '图谱画布宽 ≠ 引擎 --slide-w');
  assert.equal(G.H + 'px', engineH[1], '图谱画布高 ≠ 引擎 --slide-h');
  const reading = layoutsCSS.match(/\.slide\.reading\{padding:([^;]+);/)[1].trim().split(/\s+/);
  assert.deepEqual([G.padT, G.padX, G.padB], reading.map(v => parseInt(v, 10)), '图谱内边距 ≠ .slide.reading 的 padding');
  assert.equal(G.contentW, G.W - G.padX * 2, '图谱内容宽与画布/内边距不自洽');
  assert.equal(G.contentH, G.H - G.padT - G.padB, '图谱内容高与画布/内边距不自洽');
  const tokens = typography.css(PRESET).match(/:root\{([^}]*)\}/)[1];
  const tokenOf = name => tokens.match(new RegExp('(?:^|;)' + name + ':([^;]+)'))[1].trim();
  assert.equal(atlas.match(/--fs-title:([^;]+);/)[1], tokenOf('--fs-title'), '--fs-title 与排印预设不一致');
  assert.equal(atlas.match(/--lh-title:([^;]+);/)[1], tokenOf('--lh-title'), '--lh-title 与排印预设不一致');
  for (const t of ['--fs-body', '--fs-subtitle', '--fs-note', '--fs-data', '--fs-table-head', '--fs-exhibit-title', '--fs-annotation'])
    assert.equal(atlas.match(new RegExp(t + ':([^;]+);'))[1], tokenOf(t), t + ' 与排印预设不一致');
  assert.equal(atlas.match(/--font-title:([^;]+);/)[1], tokenOf('--font-title'), '--font-title 与排印预设不一致');
  assert.equal(atlas.match(/--font-body:([^;]+);/)[1], tokenOf('--font-body'), '--font-body 与排印预设不一致');
  const weight = typography.get(PRESET).weights.title;
  assert.equal(Number(atlas.match(/\.slide__title\{[^}]*font-weight:(\d+)/)[1]), weight, '标题字重 ≠ 排印预设');
  assert.equal(G.contentH, 662, '内容盒应为 1200×662');
  results.canvas = [G.W, G.H, G.contentW, G.contentH].join('×');
}

/* ——— 浏览器部分 ——— */
async function browserChecks() {
  const {pathToFileURL} = require('node:url');
  const pw = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
  const browser = await pw.chromium.launch();
  const fails = [];
  try {
    const page = await browser.newPage({viewport: {width: 1600, height: 1000}});
    const errors = [];
    page.on('pageerror', e => errors.push('pageerror: ' + e.message));
    page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
    const FILE = pathToFileURL(path.join(ROOT, 'assets/layout-atlas.html')).href;

    for (const e of CAT) {
      await page.goto(FILE + '#' + encodeURIComponent(e.id));
      await page.waitForTimeout(80);
      const shot = await page.evaluate(() => {
        const stage = document.getElementById('stage');
        const s = stage.getBoundingClientRect();
        const k = stage.offsetWidth ? s.width / stage.offsetWidth : 1;
        const rel = el => { const b = el.getBoundingClientRect();
          return {x: (b.x - s.x) / k, y: (b.y - s.y) / k, w: b.width / k, h: b.height / k}; };
        const regions = [...document.querySelectorAll('.region')];
        return {
          regions: regions.map(el => ({slot: el.dataset.slot, role: el.dataset.role, box: rel(el),
            container: getComputedStyle(el.parentElement).display,
            containerCols: getComputedStyle(el.parentElement).gridTemplateColumns})),
          rowsH: document.querySelector('.rows').getBoundingClientRect().height / k,
          stageW: stage.scrollWidth, stageH: stage.scrollHeight,
          titleH: document.querySelector('.slide__title').offsetHeight / k,
          tracker: rel(document.querySelector('.slide__tracker')),
          note: document.querySelector('.ov__note') ? rel(document.querySelector('.ov__note')) : null,
          thumbs: document.querySelectorAll('.nav__item').length,
          multiRow: [...document.querySelectorAll('.row')].filter(rw => getComputedStyle(rw).gridTemplateRows.split(' ').length !== 1).length
        };
      });
      if (shot.regions.length !== e.regions.length) { fails.push(e.id + '：区数 ' + shot.regions.length + ' ≠ ' + e.regions.length); continue; }
      shot.regions.forEach((seen, k) => {
        const want = e.regions[k];
        if (seen.slot !== want.slot || seen.role !== want.role) fails.push(e.id + ' region[' + k + '] data 属性 ' + seen.slot + '/' + seen.role + ' ≠ ' + want.slot + '/' + want.role);
        // 安全区 (40,32)–(1240,694)：越界就是布局错乱，溢出会被 overflow:hidden 藏起来看不见
        if (seen.box.x < 39.5 || seen.box.y < 31.5 || seen.box.x + seen.box.w > 1240.5 || seen.box.y + seen.box.h > 694.5)
          fails.push(e.id + ' region[' + k + '] 越出安全区 ' + JSON.stringify(seen.box, (x, v) => typeof v === 'number' ? Math.round(v) : v));
        if (seen.box.w < 1 || seen.box.h < 1) fails.push(e.id + ' region[' + k + '] 零尺寸');
        if (e.build.kind === 'class') {
          const container = seen.container;
          if (container !== 'grid') fails.push(e.id + ' region[' + k + '] 的容器 display=' + container + '，class 结构必须是 grid');
        }
        if (seen.containerCols === 'none') fails.push(e.id + ' region[' + k + '] 的容器没有列模板（G-LAYOUT-MISSING）');
      });
      if (shot.multiRow) fails.push(e.id + '：.row 被自动放置撑成 ' + shot.multiRow + ' 个多行容器（place 未钉住行号）');
      if (shot.stageW > 1280) fails.push(e.id + '：stage scrollWidth ' + shot.stageW + ' > 1280');
      if (shot.stageH > 720) fails.push(e.id + '：stage scrollHeight ' + shot.stageH + ' > 720');
      if (shot.thumbs !== CAT.length) fails.push(e.id + '：导航缩略图 ' + shot.thumbs + ' ≠ ' + CAT.length);
      // 顶栏注释不能压住页面眉标：两者都在页边距带里，靠左摆就会叠字
      if (shot.note && shot.note.x < shot.tracker.x + shot.tracker.w && shot.note.y < shot.tracker.y + shot.tracker.h && shot.tracker.y < shot.note.y + shot.note.h)
        fails.push(e.id + '：安全区注释与页面眉标重叠');
      // 容量核算：预算由实际渲染出的标题行数推导，不写死数字
      const lines = shot.titleH / (32 * 1.28);
      if (Math.abs(lines - Math.round(lines)) > 0.02) fails.push(e.id + '：标题高 ' + shot.titleH + ' 不是行高 40.96 的整数倍');
      const budget = 662 - (Math.round(lines) * 32 * 1.28 + 8 + 15 * 1.45) - 16 - 20 - (12 * 1.35 + 12);
      if (Math.abs(shot.rowsH - budget) > 1.2) fails.push(e.id + '：主体高 ' + shot.rowsH.toFixed(2) + ' ≠ 预算 ' + budget.toFixed(2) + '（标题 ' + Math.round(lines) + ' 行／来源在 body 内）');
    }

    // 标题行数与来源位置两个开关，直接给出 527.1 / 486.1 / 547.1 / 506.1 四个容量
    await page.goto(FILE + '#' + encodeURIComponent(CAT[0].id));
    const rowsH = async () => page.evaluate(() => document.querySelector('.rows').getBoundingClientRect().height);
    const expect = [[1, true, 527.09], [2, true, 486.13], [1, false, 547.09], [2, false, 506.13]];
    for (const [lines, srcIn, want] of expect) {
      await page.click('#tlines button[data-lines="' + lines + '"]');
      if (srcIn) await page.check('#togSrc'); else await page.uncheck('#togSrc');
      await page.waitForTimeout(60);
      const got = await rowsH();
      if (Math.abs(got - want) > 1.2) fails.push('标题 ' + lines + ' 行／来源' + (srcIn ? '内' : '外') + '：主体高 ' + got.toFixed(2) + ' ≠ ' + want);
    }

    // 三模式都要能渲染；线框模式每区都要有 slot · role · span 文案
    for (const mode of ['content', 'wire', 'contract']) {
      await page.click('#modes button[data-mode="' + mode + '"]');
      await page.waitForTimeout(60);
      const info = await page.evaluate(() => ({
        mode: document.querySelector('#modes button[aria-pressed="true"]').dataset.mode,
        regions: document.querySelectorAll('.region').length,
        wire: [...document.querySelectorAll('.region')].every(el => /·/.test(el.textContent) && /span/.test(el.textContent)),
        pres: document.querySelectorAll('.contract pre').length
      }));
      if (info.mode !== mode) fails.push('切换到 ' + mode + ' 模式失败');
      if (mode === 'wire' && !info.wire) fails.push('线框模式缺 slot · role · span 文案');
      if (mode === 'contract' && info.pres < 4) fails.push('契约模式只有 ' + info.pres + ' 个 pre 块');
    }
    await page.click('#modes button[data-mode="wire"]');
    await page.click('#togTracks');
    await page.waitForTimeout(60);
    const tracks = await page.evaluate(() => document.querySelectorAll('.ov__col').length);
    if (tracks && tracks !== 12) fails.push('栏轨道数 ' + tracks + ' ≠ 12');
    await page.click('#btnOverview');
    await page.waitForTimeout(60);
    const cards = await page.evaluate(() => document.querySelectorAll('.ovcard').length);
    if (cards !== CAT.length) fails.push('总览卡片 ' + cards + ' ≠ ' + CAT.length);

    if (errors.length) fails.push('页面报错：' + errors.slice(0, 5).join(' | '));
    results.browser = {entries: CAT.length, failures: fails.length};
  } finally {
    await browser.close();
  }
  return fails;
}

(async () => {
  if (process.argv.includes('--browser')) {
    const fails = await browserChecks();
    results.browser_failures = fails.length;
    fails.slice(0, 40).forEach(f => console.error('  - ' + f));
    assert.equal(fails.length, 0, '图谱浏览器实测有 ' + fails.length + ' 项不通过（明细见上）');
  }
  console.log(JSON.stringify({pass: true, ...results}));
})().catch(error => { console.error(error.message); process.exitCode = 1; });
