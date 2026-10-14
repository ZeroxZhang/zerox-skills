/* 单页自查的门禁反例：它是制作期工具，必须"只报看的那一页、只出那一页的图"，
   而且不能产出任何可被当成交付依据的东西（没有 audit.json、没有证据清单）。
   同时证明它真的会拦人：有阻塞缺陷的那一页必须退出非零，不能一律 PASS。 */
'use strict';
const fs = require('node:fs'), path = require('node:path'), os = require('node:os'), assert = require('node:assert/strict');
const {spawnSync} = require('node:child_process');
const {assemble} = require('./assemble_deck.cjs');

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'deck-preview-'));
const run = (...args) => spawnSync(process.execPath, [path.join(__dirname, 'preview_page.cjs'), ...args], {encoding: 'utf8', maxBuffer: 20 * 1024 * 1024});
const listing = out => fs.readdirSync(out).sort();
const slide = (page, id, proves, body) => '<section class="slide reading" data-page-id="' + id + '" data-frame-boundary="space" data-form="html.text" data-proves="' + proves + '"><header class="slide__header"><h1 class="slide__title">第' + page + '页</h1></header><div class="slide__body" style="align-content:start">' + body + '</div><div class="slide__page">' + page + '</div></section>';

(async () => {
  try {
    const pages = path.join(dir, 'pages.html'), deck = path.join(dir, 'deck.html');
    fs.writeFileSync(path.join(dir, 'pages.json'), JSON.stringify({version: 1, pages: [{page: 1, proves: '干净页不应报阻塞', form: 'html.text'}, {page: 2, proves: '过小正文必须被当场拦下', form: 'html.text'}]}));
    // 密度档位写 normal：这份夹具每页只有一行结论，考的是预览的阻塞与非阻塞判定，不是版式密度。
    fs.writeFileSync(path.join(dir, 'task.json'), JSON.stringify({workMode: 'editorial', complexity: 'simple', critical: [], densityPolicy: 'normal', pages: {record: 'pages.json'}}));
    fs.writeFileSync(pages, slide(1, 'clean', '干净页不应报阻塞', '<div id="value-clean">样本比例 38%</div>') + slide(2, 'dense', '过小正文必须被当场拦下', '<div id="value-dense">样本比例 38%</div>'));
    await assemble({pagesFile: pages, outputFile: deck, contractFile: path.join(dir, 'task.json')});
    // 只在第 2 页注入一个真实缺陷：把正文压到 8px，低于可读下限。
    fs.writeFileSync(path.join(dir, 'deck-bad.html'), fs.readFileSync(deck, 'utf8').replace('</head>', '<style>[data-page-id="dense"] #value-dense{font-size:8px !important}</style></head>'));

    // 干净稿：只看第 2 页，就只出第 2 页的图，且不留下任何验收产物。
    const one = path.join(dir, 'one');
    const okRun = run(deck, '2', '--out', one, '--json');
    assert.equal(okRun.status, 0, '干净页不该退出非零：' + okRun.stdout + okRun.stderr);
    const ok = JSON.parse(okRun.stdout);
    assert.deepEqual(ok.pages, [2], '只该看被点名的页');
    assert.deepEqual(ok.errors, [], '干净页不该有阻塞项：' + JSON.stringify(ok.errors));
    assert.deepEqual(listing(one), ['p02.png'], '只该产出被点名页的截图');
    assert.equal(fs.existsSync(path.join(one, 'audit.json')), false, '单页自查不得产出 audit.json');
    assert.equal(typeof ok.manual, 'object', '需要人工判断的路径要原样带出，不能被压成"已检查"');

    // 整册：--all 覆盖每一页。
    const all = path.join(dir, 'all');
    assert.equal(run(deck, '--all', '--out', all).status, 0, '--all 应能跑通');
    assert.deepEqual(listing(all), ['p01.png', 'p02.png'], '--all 要覆盖每一页');

    // 缺陷页必须退出非零并点名；同一份稿的干净页仍然退出 0——说明"只看这一页"是真的在分页判定。
    const bad = path.join(dir, 'bad');
    const badRun = run(path.join(dir, 'deck-bad.html'), '2', '--out', bad);
    assert.equal(badRun.status, 1, '有阻塞缺陷的页必须退出非零');
    assert.match(badRun.stdout + badRun.stderr, /UNREADABLE-TEXT/, '缺陷要按检查项点名，而不是只给一句失败');
    assert.equal(run(path.join(dir, 'deck-bad.html'), '1', '--out', path.join(dir, 'bad1')).status, 0, '同一份稿的第 1 页没被改坏，不该被牵连');

    // 越界页码当场说清，并落到"没有可预览的页码"，而不是静默跑完。
    const oob = run(deck, '9', '--out', path.join(dir, 'oob'));
    assert.equal(oob.status, 1, '越界页码不能静默通过');
    assert.match(oob.stdout + oob.stderr, /没有可预览的页码/);
    assert.match(run(deck, '--out', path.join(dir, 'none')).stderr, /需要页码或 --all/, '不给页码要报用法，而不是默认跑全册');

    console.log('PASS preview page: 只出点名页的图 / 不产出验收产物 / 缺陷页拦下且不牵连相邻页 / 越界与漏参当场拒绝');
  }
  finally { fs.rmSync(dir, {recursive: true, force: true}); }
})().catch(error => { console.error(error); process.exitCode = 1; });
