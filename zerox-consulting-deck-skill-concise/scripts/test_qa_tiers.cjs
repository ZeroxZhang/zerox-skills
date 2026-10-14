/* QA 分档的门禁反例：迭代与冒烟档是制作期工具，不能产出任何可被当成交付依据的东西。
   这里同时证明"默认档仍然是原来的全量验收"，避免分档把验收悄悄降级。 */
'use strict';
const fs = require('node:fs'), path = require('node:path'), os = require('node:os'), assert = require('node:assert/strict');
const {spawnSync} = require('node:child_process');
const {assemble} = require('./assemble_deck.cjs');
const {packageDelivery} = require('./package_delivery.cjs');

const root = path.resolve(__dirname, '..'), dir = fs.mkdtempSync(path.join(os.tmpdir(), 'deck-qa-tiers-'));
const run = (args, env = process.env) => spawnSync(process.execPath, [path.join(__dirname, 'qa_deck.cjs'), ...args], {encoding: 'utf8', env, maxBuffer: 20 * 1024 * 1024});
const auditOf = out => JSON.parse(fs.readFileSync(path.join(out, 'audit.json'), 'utf8'));
const listing = out => fs.readdirSync(out).sort();

(async () => {
  try {
    const pages = path.join(dir, 'pages.html'), deck = path.join(dir, 'deck.html'), task = path.join(dir, 'task.json'), record = path.join(dir, 'pages.json');
    fs.writeFileSync(record, JSON.stringify({version: 1, pages: [{page: 1, proves: '样本比例不能被读成最终收入比', form: 'html.text'}]}));
    // 密度档位显式写 normal：这份夹具只有一页、正文区只有几十像素内容，考的是分档而不是密度。
    // 真实报告默认 compact——要松排版必须自己声明，不能靠不写来默认松。
    fs.writeFileSync(task, JSON.stringify({workMode: 'editorial', complexity: 'simple', critical: [], densityPolicy: 'normal', pages: {record: 'pages.json'}}));
    // 正文里放一个真实展品：打印复检必须对着屏幕上的实际图元核，而不是对着空页自证。
    fs.writeFileSync(pages, '<section class="slide reading" data-page-id="evidence" data-frame-boundary="space" data-form="html.text" data-proves="样本比例不能被读成最终收入比"><header class="slide__header"><h1 class="slide__title">分档验证</h1></header><div class="slide__body" style="align-content:start"><div id="value">样本比例 38%</div><svg viewBox="0 0 120 20" width="120" height="20" role="img"><rect x="0" y="4" width="80" height="12" fill="#123456"/></svg></div><div class="slide__page">1</div></section>');
    await assemble({pagesFile: pages, outputFile: deck, contractFile: task});

    // 迭代档：只出被点名的页，不出 PDF、不出总体图、不出证据清单。
    const iter = path.join(dir, 'iter');
    assert.equal(run([deck, iter, '--tier', 'iteration', '--pages', '1']).status, 0, '迭代档应能跑通');
    const iterAudit = auditOf(iter);
    assert.equal(iterAudit.tier, 'iteration');
    assert.equal(iterAudit.acceptance.complete, false, '迭代档不能自称完成验收');
    assert.ok(iterAudit.acceptance.missingStages.includes('PDF产物校验'), '缺项要写在 audit 里：' + JSON.stringify(iterAudit.acceptance));
    assert.equal(iterAudit.evidenceManifest, null, '迭代档不得产出证据清单');
    assert.equal(iterAudit.pdfArtifact.skipped, true);
    assert.equal(iterAudit.printCheck.status, 'NOT_CHECKED', '迭代档不做打印媒体复检');
    assert.deepEqual(listing(iter), ['audit.json', 'p01.png'], '迭代档只应产出被点名页的截图与 audit');

    // 冒烟档：全页几何 + 打印复检 + 总览，仍然不出 PDF 与证据清单。
    const smoke = path.join(dir, 'smoke');
    assert.equal(run([deck, smoke, '--tier', 'smoke']).status, 0, '冒烟档应能跑通');
    const smokeAudit = auditOf(smoke);
    assert.equal(smokeAudit.tier, 'smoke');
    assert.equal(smokeAudit.acceptance.complete, false);
    assert.equal(smokeAudit.evidenceManifest, null, '冒烟档不得产出证据清单');
    assert.equal(smokeAudit.printCheck.expected, 1, '冒烟档要对着实际展品做打印媒体复检');
    assert.deepEqual(smokeAudit.printCheck.missing, []);
    assert.deepEqual(listing(smoke), ['audit.json', 'overview.png', 'p01.png'], '冒烟档不应产出 PDF');

    // 越界用法必须被当场拒绝，而不是跑一半再失败。
    assert.notEqual(run([deck, path.join(dir, 'bad1'), '--pages', '1']).status, 0, '--pages 不能用于验收档');
    assert.match(run([deck, path.join(dir, 'bad1'), '--pages', '1']).stderr, /只用于 iteration 档/);
    assert.match(run([deck, path.join(dir, 'bad2'), '--tier', 'fast']).stderr, /tier 须为/);
    assert.match(run([deck, path.join(dir, 'bad3'), '--tier', 'iteration', '--pages', '9']).stderr, /没有可检查的页码/);
    // iteration 的缺项清单假定"只跑了点名的页"；不点名页码却跑整册，清单就会与实跑不符。
    assert.match(run([deck, path.join(dir, 'bad4'), '--tier', 'iteration']).stderr, /要指定 --pages/, '迭代档不点名页码必须被拒绝');

    // 默认档必须还是原来的全量验收：有 PDF、有证据清单、complete。
    const full = path.join(dir, 'full');
    assert.equal(run([deck, full]).status, 0, '验收档应能跑通');
    const fullAudit = auditOf(full);
    assert.equal(fullAudit.tier, 'acceptance');
    assert.deepEqual(fullAudit.acceptance, {complete: true, tier: 'acceptance', missingStages: []});
    assert.equal(fullAudit.evidenceManifest.entries.length, 2, '验收档仍要产出双媒介逐页证据');
    assert.ok(fs.existsSync(path.join(full, 'deck.pdf')), '验收档仍要导出实际 PDF');

    // 非验收档的 audit 一律不能作为打包依据，而且是点名拒绝。
    const forged = path.join(dir, 'forged');
    fs.mkdirSync(forged);
    fs.copyFileSync(path.join(full, 'audit.json'), path.join(forged, 'audit.json'));
    fs.copyFileSync(path.join(full, 'deck.pdf'), path.join(forged, 'deck.pdf'));
    const iterTier = JSON.parse(fs.readFileSync(path.join(forged, 'audit.json'), 'utf8'));
    iterTier.tier = 'iteration';
    iterTier.acceptance = {complete: false, tier: 'iteration', missingStages: ['PDF产物校验', '断网一致性']};
    iterTier.input = deck;
    fs.writeFileSync(path.join(forged, 'audit.json'), JSON.stringify(iterTier));
    assert.throws(() => packageDelivery({htmlFile: deck, pdfFile: path.join(forged, 'deck.pdf'), outputDir: path.join(dir, 'delivery'), baseName: 'x', auditFile: path.join(forged, 'audit.json')}), /iteration 档/, '迭代档 audit 不能作为交付依据');

    console.log('PASS qa tiers: 迭代只出点名页 / 冒烟做打印复检 / 越界用法当场拒绝 / 默认档仍是全量验收 / 非验收档 audit 不能打包');
  }
  finally { fs.rmSync(dir, {recursive: true, force: true}); }
})().catch(error => { console.error(error); process.exitCode = 1; });
