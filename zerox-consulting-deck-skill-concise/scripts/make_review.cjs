/* 复核记录骨架生成器。
   复核结构里有一大半是机械内容：全页双媒介的证据 id、逐条告警原文、绑定摘要。
   手抄这些既耗时又毫无判断价值，而"手写 56 条 id 比真看 56 张图便宜"正是覆盖造假的土壤。
   这里把机械部分填好，人只填判断：逐页所见、四层依据、告警处置、问题清单。

   用法：
     node scripts/make_review.cjs <audit.json> <输出.json> --role author|independent --reviewer 名字 [--pages 1,2]
     node scripts/make_review.cjs <audit.json> <输出.json> --role independent --reviewer 名字 --inherit <旧audit> <旧review>
   已存在的输出不会覆盖，除非加 --force。 */
'use strict';
const fs = require('node:fs'), path = require('node:path');
const contract = require('./report_contract.cjs');

function parseArgs(argv) {
  const out = {input: null, output: null, role: null, reviewer: null, pages: null, inherit: null, force: false};
  const positional = [];
  for (let i = 0; i < argv.length; i++) {
    const v = argv[i];
    if (v === '--role') out.role = argv[++i];
    else if (v === '--reviewer') out.reviewer = argv[++i];
    else if (v === '--pages') out.pages = String(argv[++i] || '').split(',').map(t => Number(t.trim()));
    else if (v === '--inherit') out.inherit = [argv[++i], argv[++i]];
    else if (v === '--force') out.force = true;
    else if (v && !v.startsWith('--')) positional.push(v);
    else throw Error('未知参数: ' + v);
  }
  out.input = positional[0]; out.output = positional[1];
  if (!out.input || !out.output) throw Error('用法: node scripts/make_review.cjs <audit.json> <输出.json> --role author|independent --reviewer 名字 [--pages 1,2] [--inherit 旧audit 旧review] [--force]');
  if (!['author', 'independent'].includes(out.role)) throw Error('--role 须为 author 或 independent');
  if (!out.reviewer || !out.reviewer.trim()) throw Error('--reviewer 不能为空：复核记录要写清是谁在什么条件下做的');
  if (out.pages && out.pages.some(n => !Number.isInteger(n) || n < 1)) throw Error('--pages 需要正整数页码，如 --pages 1,3');
  return out;
}

const rel = (from, to) => path.relative(path.dirname(from), to).split(path.sep).join('/') || '.';

function main(argv) {
  const options = parseArgs(argv);
  const auditFile = path.resolve(options.input), outputFile = path.resolve(options.output);
  if (fs.existsSync(outputFile) && !options.force) throw Error('输出已存在：' + outputFile + '（那是一份已经填过判断的复核记录，不要覆盖它；确要重来加 --force）');
  const audit = JSON.parse(fs.readFileSync(auditFile, 'utf8'));
  const manifest = audit.evidenceManifest?.entries;
  if (!Array.isArray(manifest) || !manifest.length) throw Error('audit 缺少证据清单：先跑验收档 qa_deck，迭代/冒烟档不能作为复核依据');

  const all = Array.from({length: audit.pages}, (_, i) => i + 1);
  const pages = options.pages ? options.pages.filter(n => n <= audit.pages) : all;
  if (!pages.length) throw Error('--pages 没有落在 1–' + audit.pages + ' 范围内');
  const evidenceFor = list => manifest.filter(e => list.includes(e.page)).map(e => ({id: e.id}));

  const coverage = [];
  const fresh = {reviewer: options.reviewer.trim(), independence: options.role, layers: ['page', 'exhibit', 'annotation', 'typography'],
    htmlPages: pages, pdfPages: pages, evidence: evidenceFor(pages),
    attestation: pages.map(page => ({page, note: ''}))};
  const notes = [];

  if (options.inherit) {
    const [oldAuditArg, oldReviewArg] = options.inherit;
    const oldAuditFile = path.resolve(oldAuditArg), oldReviewFile = path.resolve(oldReviewArg);
    for (const file of [oldAuditFile, oldReviewFile]) if (!fs.existsSync(file)) throw Error('继承来源不存在：' + file);
    const oldAudit = JSON.parse(fs.readFileSync(oldAuditFile, 'utf8'));
    const oldReview = JSON.parse(fs.readFileSync(oldReviewFile, 'utf8'));
    /* 继承要求旧 audit 记录的产物**仍然可核**。就地重建 deck.html/deck.pdf 会让这项立刻失败，
       而那是所有人的默认做法——所以在这里先拦，把"要去留档快照"这句话讲在前面，
       而不是让人写完一份复核才在 review_contract 里收到"旧产物缺失/已修改"。 */
    const stale = [];
    for (const medium of ['html', 'pdf']) {
      const artifact = oldAudit[medium + 'Artifact'];
      if (!artifact?.path) { stale.push(medium + '（旧 audit 未记录产物）'); continue; }
      const file = path.resolve(path.dirname(oldAuditFile), artifact.path);
      if (!fs.existsSync(file)) stale.push(medium + ' 产物已不在：' + file);
      else if (contract.fileHash(file) !== artifact.sha256) stale.push(medium + ' 产物已改变：' + file);
    }
    if (stale.length) throw Error('不能从这次审查继承：' + stale.join('；') +
      '。\n继承核的是"旧审查当时看的那份产物"，就地重建 deck 会让它失效，而就地重建是默认做法。' +
      '注意 audit 记录的是**绝对路径**，所以即便把 audit 与产物一起留档，校验器仍会 `path.resolve(归档目录, 绝对路径)` 回到原位置核原件——' +
      '留档副本不会被核到。要用继承，归档件必须是在留档时**重写过产物路径并重新记录摘要**的那一份，技能目前不产出这样的归档件。' +
      '所以本轮的可行做法是按完整覆盖重做复核；继承留给"归档件从这一轮起被正确产出"之后的轮次。');
    // 旧审查会被递归校验，且不按 partial 放行：它必须是绑在同一份留档 audit 上的两角色齐全件。
    const oldRoles = new Set((Array.isArray(oldReview.coverage) ? oldReview.coverage : []).map(c => c.independence));
    if (!['author', 'independent'].every(role => oldRoles.has(role))) throw Error('不能从这次审查继承：旧审查只覆盖了 ' + [...oldRoles].join('、') +
      '，而继承会递归校验它、并像终稿一样要求两个角色齐全。请改用绑在同一份留档 audit 上的两角色齐全聚合件。');
    const oldEntries = new Map((oldAudit.evidenceManifest?.entries || []).map(e => [e.id, e]));
    // 能不能继承由摘要决定，不由说明决定：四个逐页摘要与页号全等才算未变。
    const keys = ['pageSha256', 'pageStyleSha256', 'dependenciesSha256', 'sha256', 'page'];
    const unchanged = [], changed = [];
    for (const page of pages) {
      const id = 'html:page-' + (manifest.find(e => e.page === page && e.medium === 'html')?.pageId || page);
      const cur = manifest.find(e => e.id === id), prev = oldEntries.get(id);
      const same = cur && prev && keys.every(k => cur[k] === prev[k]);
      (same ? unchanged : changed).push(page);
    }
    const oldCovers = id => Array.isArray(oldReview.coverage) && oldReview.coverage.some(c => c.independence === options.role && (c.evidence || []).some(e => e.id === id));
    const inheritable = unchanged.filter(page => {
      const id = manifest.find(e => e.page === page && e.medium === 'html')?.id;
      return id && oldCovers(id);
    });
    const mustReview = pages.filter(page => !inheritable.includes(page));
    if (inheritable.length) {
      coverage.push({reviewer: options.reviewer.trim(), independence: options.role, layers: ['page', 'exhibit', 'annotation', 'typography'],
        htmlPages: inheritable, pdfPages: inheritable, evidence: evidenceFor(inheritable),
        inheritedFrom: {basis: '', audit: {path: rel(outputFile, oldAuditFile), sha256: contract.fileHash(oldAuditFile)},
          review: {path: rel(outputFile, oldReviewFile), sha256: contract.fileHash(oldReviewFile)}}});
      notes.push('继承条目已有 ' + inheritable.length + ' 页（第 ' + inheritable.join('、') + ' 页）：**必须填 inheritedFrom.basis**，说明本轮改了什么、凭什么认定这些页未变。');
    }
    fresh.htmlPages = mustReview; fresh.pdfPages = mustReview; fresh.evidence = evidenceFor(mustReview);
    fresh.attestation = mustReview.map(page => ({page, note: ''}));
    if (changed.length) notes.push('摘要变化、必须重新审的页：' + changed.join('、') + (inheritable.length ? '' : '（全部页都要重新看）'));
  }
  if (fresh.htmlPages.length) coverage.push(fresh);

  const review = {
    schemaVersion: 3,
    status: 'incomplete',
    reviewer: options.reviewer.trim(),
    independence: options.role,
    // 独立复核必须来自干净上下文；fork 会继承作者推理，那时只能如实降为 author。
    isolation: options.role === 'independent' ? 'fresh-context' : 'same-session',
    htmlSha256: audit.htmlArtifact?.sha256,
    pdfSha256: audit.pdfArtifact?.sha256,
    auditSha256: contract.hash(contract.stable(audit)),
    coverage,
    warningReview: (audit.warnings || []).map(warning => ({warning, status: '', note: ''})),
    checks: {analysis: {status: 'not_reviewed', basis: ''}, evidence: {status: 'not_reviewed', basis: ''}, visual: {status: 'not_reviewed', basis: ''}},
    issues: []
  };
  fs.mkdirSync(path.dirname(outputFile), {recursive: true});
  fs.writeFileSync(outputFile, JSON.stringify(review, null, 2));

  const todo = [
    'coverage.attestation：每页写一条**只能来自实际所见的**短记录（例如"左下象限空着""两条柱几乎等高"）。全篇不得重复——这是引用与真看过的唯一分界。',
    'checks.analysis / evidence / visual：填 status 与 basis。basis 写实际做了什么（看了哪些页、复算了哪些数），不写"已检查，无问题"。status 只表示这一层做完了，问题进 issues。',
    'warningReview：逐条填 status（accepted|fixed）与 note。note 要能被核对——写清按实际尺寸看到了什么，不要一条理由复制到多条上。',
    'issues：查到的问题用 {severity: minor|major|blocking, status: open|resolved, description} 写进来。major 与 blocking 必须 resolved 才能交付。没有问题就留空数组，表示检查过。',
    'status 改 complete 之前，自行跑一次 `review_contract.validate` 或等聚合时报错——占位与空值都会被点名。'
  ].concat(notes);
  console.log(JSON.stringify({written: outputFile, pages: pages.length, coverageEntries: coverage.length, warnings: review.warningReview.length, todo}, null, 2));
}

if (require.main === module) { try { main(process.argv.slice(2)); } catch (e) { console.error(e.message); process.exitCode = 1; } }
module.exports = {main};
