/* 页级失效半径的定向验证：证明"改一页只作废一页"，且证明不了作用域的一律保守归全局。
   上半段用合成快照直接测 manifest，下半段在真实浏览器里测 captureDocument 的分桶。 */
'use strict';
const fs = require('node:fs'), path = require('node:path'), os = require('node:os'), assert = require('node:assert/strict');
const {pathToFileURL} = require('node:url');
const {hash, stable} = require('./report_contract.cjs');
const auditEvidence = require('./audit_evidence.cjs');
let playwright;
try { playwright = require('playwright'); } catch { playwright = require(process.env.PLAYWRIGHT_MODULE || 'playwright'); }

const root = path.resolve(__dirname, '..'), dir = fs.mkdtempSync(path.join(os.tmpdir(), 'deck-evidence-scope-'));
const stylesOf = snapshot => snapshot.pages.map(p => hash(stable(p.styles)));
const contentOf = snapshot => snapshot.pages.map(p => hash(p.content));

/* 上半段：manifest 只做逐页绑定，不启动浏览器。 */
function manifestScope() {
  const shots = ['p01.png', 'p02.png'];
  for (const name of shots) fs.writeFileSync(path.join(dir, name), 'synthetic render ' + name);
  const snapshot = {
    pages: [
      {page: 1, pageId: 'p1', content: '<section class="slide" data-proves="a"></section>', styles: ['#p1 .slide__title{letter-spacing:0.01em}']},
      {page: 2, pageId: 'p2', content: '<section class="slide" data-proves="b"></section>', styles: ['#p2 .slide__title{letter-spacing:0.02em}']}
    ],
    dependencies: {styles: 'GLOBAL-CSS', scripts: [], fonts: {faces: []}, ratio: '16x9'}
  };
  const rows = [{page: 1, screenshot: shots[0]}, {page: 2, screenshot: shots[1]}];
  const artifacts = {html: {sha256: 'h'.repeat(64)}, pdf: {sha256: 'p'.repeat(64)}};
  const task = {kind: 'report', theme: 'mckinsey', typography: 'serif-report-bold', ratio: '16x9', pages: {record: 'pages.json', sha256: 'a'.repeat(64)}};
  const build = (t, snap = snapshot) => auditEvidence.manifest(snap, rows, [], artifacts, t, dir, {browser: 'test', viewport: {width: 1400, height: 820}});
  const base = build(task);
  assert.equal(base.entries.length, 2, '每个媒介/页各一条证据');
  assert.match(base.entries[0].pageStyleSha256, /^[a-f0-9]{64}$/, '逐页样式指纹必须是摘要');
  assert.notEqual(base.entries[0].pageStyleSha256, base.entries[1].pageStyleSha256, '不同页的样式作用域必须是不同的指纹');
  assert.equal(base.entries[0].pageSha256, hash(snapshot.pages[0].content));
  // 逐页合同只绑定在页上，不进入公共依赖；改 pages.json 不该作废全篇。
  const pagesTouched = build({...task, pages: {record: 'pages.json', sha256: 'b'.repeat(64)}});
  assert.equal(pagesTouched.dependenciesSha256, base.dependenciesSha256, 'pages 记录变更不应进入公共依赖');
  // deck 级身份仍然一票否决。
  for (const key of ['theme', 'typography', 'ratio', 'kind']) {
    assert.notEqual(build({...task, [key]: 'changed-' + key}).dependenciesSha256, base.dependenciesSha256, key + ' 变更必须改变公共依赖');
  }
  // 共享样式改变＝所有页面一起失效。
  const restyled = build(task, {...snapshot, dependencies: {...snapshot.dependencies, styles: 'GLOBAL-CSS-CHANGED'}});
  assert.notEqual(restyled.dependenciesSha256, base.dependenciesSha256, '公共样式改变必须改变公共依赖');
  assert.deepEqual(restyled.entries.map(e => e.pageStyleSha256), base.entries.map(e => e.pageStyleSha256), '公共样式改变不改写页级样式指纹');
  // 快照缺逐页样式作用域时必须报错，不能悄悄退回全局。
  assert.throws(() => build(task, {...snapshot, pages: snapshot.pages.map(({styles, ...rest}) => rest)}), /逐页样式作用域/);
  assert.throws(() => build(task, {...snapshot, pages: [snapshot.pages[0], {...snapshot.pages[0]}]}), /data-page-id重复/);
  console.log('manifest: PASS 逐页样式指纹独立 / pages 记录不入公共依赖 / deck 级身份仍全篇失效 / 缺作用域即报错');
  return base;
}

/* 下半段：真实浏览器里的选择器作用域判定。 */
async function browserScope() {
  const browser = await playwright.chromium.launch({channel: process.env.CHROME_CHANNEL || 'chrome', headless: true});
  try {
    const page = await browser.newPage({viewport: {width: 1400, height: 820}});
    await page.goto(pathToFileURL(path.join(root, 'assets/reference_deck.html')).href, {waitUntil: 'networkidle'});
    await page.evaluate(() => window.deckReady || document.fonts.ready);
    const total = await page.locator('.slide').count();
    assert.ok(total >= 3, '参考样稿需要至少三页');
    // 目标选择器从真实 DOM 推出，避免写死 nth-child 而随样稿改版失效。
    const pageSel = await page.evaluate(() => {
      const target = document.querySelectorAll('.slide')[1], parent = target.parentElement;
      const scope = parent.id ? '#' + parent.id : parent.tagName.toLowerCase();
      return scope + ' > .slide:nth-child(' + ([...parent.children].indexOf(target) + 1) + ')';
    });
    const snap = () => page.evaluate(auditEvidence.captureDocument);
    const inject = css => page.evaluate(text => { const s = document.createElement('style'); s.textContent = text; document.head.appendChild(s); }, css);

    const before = await snap();
    assert.equal(before.pages.length, total);
    // 逐页作用域：只命中第二页的规则，不许出现在其他页的桶里，也不许进公共依赖。
    const added = (from, to, index) => to.pages[index].styles.slice(from.pages[index].styles.length);
    const expectOne = (from, to, index, selector, property) => {
      const extra = added(from, to, index).filter(rule => rule.includes(property));
      assert.equal(extra.length, 1, '第' + (index + 1) + '页应恰好新增一条含 ' + property + ' 的规则，实际 ' + JSON.stringify(added(from, to, index)));
      assert.ok(extra[0].trim().startsWith(selector), '新规则的选择器应是 ' + selector + '，实际 ' + extra[0]);
    };
    await inject(pageSel + '{--probe-self:1}');
    const scoped = await snap();
    expectOne(before, scoped, 1, pageSel, '--probe-self');
    for (const i of [0, 2]) assert.deepEqual(added(before, scoped, i), [], '其他页不应收到这条规则');
    assert.equal(scoped.dependencies.styles, before.dependencies.styles, '逐页规则不得进入公共依赖');
    // 命中该页后代的规则同样属于该页，且不得外溢。
    await inject(pageSel + ' *{--probe-descendant:1}');
    const scopedChild = await snap();
    expectOne(scoped, scopedChild, 1, pageSel + ' *', '--probe-descendant');
    for (const i of [0, 2]) assert.deepEqual(added(before, scopedChild, i), [], '后代规则不得外溢');
    // 证明不了作用域的规则一律进公共依赖，让全篇一起失效。
    const global = [
      ['body', 'body{--probe-body:1}'],
      ['根元素', ':root{--probe-root:1}'],
      ['通配', '*{--probe-all:1}'],
      ['无匹配', '.probe-not-present-xyz{--probe-none:1}'],
      ['伪元素', pageSel + '::before{content:""}'],
      ['媒体规则', '@media screen{' + pageSel + '{--probe-media:1}}']
    ];
    let previous = scopedChild;
    for (const [label, css] of global) {
      await inject(css);
      const now = await snap();
      assert.notEqual(now.dependencies.styles, previous.dependencies.styles, label + ' 必须进公共依赖（当前判成页面作用域）');
      assert.deepEqual(stylesOf(now), stylesOf(previous), label + ' 不应改写任何页级桶');
      previous = now;
    }
    // 页内容哈希只随本页 DOM 变化。
    const beforeContent = contentOf(previous);
    await page.evaluate(() => document.querySelectorAll('.slide')[1].insertAdjacentHTML('beforeend', '<span data-probe-content="1">探测</span>'));
    const afterContent = contentOf(await snap());
    assert.notEqual(afterContent[1], beforeContent[1], '本页 DOM 变化必须改变本页内容哈希');
    for (const i of [0, 2]) assert.equal(afterContent[i], beforeContent[i], '其他页内容哈希不得变化');
    console.log('captureDocument: PASS 页内规则归该页 / 后代规则不外溢 / body·:root·通配·无匹配·伪元素·@media 全部保守归全局 / 内容哈希按页隔离');
  } finally { await browser.close(); }
}

(async () => {
  try {
    manifestScope();
    await browserScope();
    console.log('PASS evidence scope: 页级失效半径成立，且判不准时一律退到全篇失效');
  } finally { fs.rmSync(dir, {recursive: true, force: true}); }
})().catch(error => { console.error(error); process.exitCode = 1; });
