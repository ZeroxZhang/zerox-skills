/* pages.json 是 S3 的机器可读产物：逐页声明这条页面证明什么、用什么形式实现。
   form 是实现入口，visual 是实际表达。这里只做结构与一致性校验，不判定形式选得好不好——那是分析取舍与目视验收。 */
'use strict';
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const forms = require('../assets/deck-forms.js');
const layer = require('../assets/annotation-layer.js');

const SLOTS = ['main', 'left', 'right', 'top', 'bottom', 'aside', 'full'];
const ROLES = ['primary', 'support', 'context', 'evidence'];
const BOOKEND_ROLES = ['cover', 'references', 'back-cover', 'divider'];
/* 真实编码族：custom 表示"实现入口未登记"，不是一个分析族，所以不计入分布——
   5 页手绘 SVG 若都记成 custom，跨族丰富度就从账面上消失了。 */
const ENCODING_FAMILIES = Object.keys(forms.familyLabels).filter(family => family !== 'custom');
/* 展品族：结构化文字没有共同维度时是正当兜底，不是一种编码选择，所以不算展品、也不要求解释。
   占比以展品页为基数——通篇文字页不该把图型占比稀释掉。 */
const EXHIBIT_FAMILIES = ENCODING_FAMILIES.filter(family => family !== 'text');
/* 单一族占据多少才算"塌缩成一个族"：绝对量到 4 页，且占展品页 30% 以上。
   三页小稿不触发；40 页里 6 页同族（15%）也不触发。 */
const FAMILY_FLOOR = 4, FAMILY_SHARE = 0.30;
/* 展品页数达到这个量级，就必须逐族交代没用上的编码。低于它就是单页或小组件稿，
   没有"跨族表达"的余地。 */
const UNUSED_REVIEW_FLOOR = 8;
const fileHash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const norm = value => String(value === undefined || value === null ? '' : value).replace(/\s+/g, ' ').trim();

function check(doc) {
  const errors = [];
  const bad = message => errors.push(message);
  if (!doc || typeof doc !== 'object' || Array.isArray(doc)) { bad('pages.json 须为对象'); return { status: 'FAIL', errors }; }
  if (doc.version !== 1) bad('pages.version 只接受 1');
  if (!Array.isArray(doc.pages) || !doc.pages.length) { bad('pages.pages 须为非空数组'); return { status: 'FAIL', errors }; }
  const seen = new Set();
  doc.pages.forEach((page, index) => {
    const at = '第 ' + (index + 1) + ' 条';
    if (!page || typeof page !== 'object') { bad(at + ' 须为对象'); return; }
    if (!Number.isInteger(page.page) || page.page < 1) bad(at + ' 缺少合法 page 序号');
    else if (seen.has(page.page)) bad('page 序号重复: ' + page.page); else seen.add(page.page);
    if (!norm(page.proves)) bad(at + '（page ' + page.page + '）缺少 proves：这页要让读者看出什么关系');
    if (page.form === 'svg.custom' && !norm(page.visual)) bad(at + ' svg.custom 必须用 visual 声明实际表达');
    if (page.visual !== undefined && (typeof page.visual !== 'string' || !norm(page.visual))) bad(at + ' visual 须为非空的实际表达名称');
    // svg.custom 是自由入口，只有作者知道它实际落在哪个编码族；不声明就会全部记进 custom，族分布随之失真。
    if (page.form === 'svg.custom' && !norm(page.encodingFamily)) bad(at + ' svg.custom 必须用 encodingFamily 声明实际编码族（' + ENCODING_FAMILIES.join('/') + '）：visual 是表达名称，encodingFamily 才是分布记账的族');
    if (page.encodingFamily !== undefined) {
      if (!ENCODING_FAMILIES.includes(page.encodingFamily)) bad(at + ' encodingFamily 须为 ' + ENCODING_FAMILIES.join('/') + (page.encodingFamily === 'custom' ? '；custom 不是可声明的族，它是"未登记"的占位' : ''));
      else if (page.form !== 'svg.custom') bad(at + ' encodingFamily 只用于 svg.custom：已登记形式的族由 form 决定，重复声明会掩盖不一致');
    }
    let entry = null;
    try { entry = forms.get(page.form); }
    catch (error) { bad(at + '（page ' + page.page + '）' + error.message); }
    if (Array.isArray(page.regions) && page.regions.length) {
      const primaries = page.regions.filter(r => r && r.role === 'primary');
      if (primaries.length !== 1) bad(at + ' regions 必须恰好有一个 role="primary"，当前 ' + primaries.length + ' 个');
      page.regions.forEach((region, r) => {
        const where = at + ' regions[' + r + ']';
        if (!region || typeof region !== 'object') { bad(where + ' 须为对象'); return; }
        if (region.form === 'svg.custom' && !norm(region.visual)) bad(where + ' svg.custom 必须用 visual 声明实际表达');
        if (region.visual !== undefined && (typeof region.visual !== 'string' || !norm(region.visual))) bad(where + ' visual 须为非空字符串');
        if (!SLOTS.includes(region.slot)) bad(where + ' slot 须为 ' + SLOTS.join('/'));
        if (!ROLES.includes(region.role)) bad(where + ' role 须为 ' + ROLES.join('/'));
        if (typeof region.span !== 'number' || !Number.isFinite(region.span) || region.span <= 0) bad(where + ' span 须为正数');
        try { forms.get(region.form); } catch (error) { bad(where + ' ' + error.message); }
      });
      if (primaries.length === 1 && primaries[0].visual !== undefined && norm(primaries[0].visual) !== norm(page.visual)) bad(at + ' 主区 visual 与 page.visual 不一致');
      if (page.form !== undefined && primaries.length === 1 && primaries[0].form !== page.form) bad(at + ' 主区形式与 page.form 不一致：' + primaries[0].form + ' ≠ ' + page.form);
    }
    // 标注准入只区分"谁负责摆位"，不再按形式族禁写：
    // 通用层自动摆位的走 annotationMode 缺省；其余形式允许手摆，但要显式声明并承担目视验收。
    // 之前的"未接入即拒绝"把作者推回少数可标注形式，反而压低了编码族的多样性。
    if (page.annotations !== undefined) {
      const auto = entry && entry.annotation === 'layer';
      const manual = page.annotationMode === 'manual';
      if (!Array.isArray(page.annotations)) bad(at + ' annotations 须为数组');
      else if (page.annotations.length && !auto && !manual) bad(at + ' 形式 ' + page.form + ' 未接入通用标注层：要在这页写 annotations，须声明 annotationMode:"manual"（标注由作者摆位，必须实际看图验收）' + (entry && entry.annotation === 'comparisons' ? '；该形式另有自带 comparisons 入口，二选一' : ''));
      else if (manual && auto) bad(at + ' 形式 ' + page.form + ' 已接入通用标注层，不需要 annotationMode:"manual"：自动摆位更可靠，去掉这个声明');
      else page.annotations.forEach((a, k) => {
        const where = at + ' annotations[' + k + ']';
        if (!a || typeof a !== 'object') { bad(where + ' 须为对象'); return; }
        if (!norm(a.id)) bad(where + ' 缺少 id：旁解读要在成稿对账、被复核引用，得有自己的标识');
        if (!norm(a.on)) bad(where + ' 缺少 on（锚点 id）');
        const kind = a.kind || 'value';
        const contract = layer.kinds[kind];
        if (!contract) bad(where + ' kind 须为 ' + layer.kindList.join('/'));
        else {
          if (contract.requiresText && !norm(a.text)) bad(where + ' kind=' + kind + ' 必须给 text');
          if (contract.requiresFrom && !norm(a.from)) bad(where + ' kind=' + kind + ' 必须给 from');
        }
        if (a.of !== undefined && !norm(a.of)) bad(where + ' of 不能为空');
      });
    }
    // 外部能力 ID 不限制自定义绘制；采用 plan 的版本与落实由专门检查器和实际看图核对。
    if (page.planner !== undefined && (!page.planner || !norm(page.planner.capability_id))) bad(at + ' planner 须写 capability_id');
    if (page.repetitionReason !== undefined && !norm(page.repetitionReason)) bad(at + ' repetitionReason 不能为空');
    // 图型不因容量不足改表：合同里不再有降级出口，放不下时在同一表达内重排、分面或换实现。
    if (page.fallback !== undefined) bad(at + ' 已取消 fallback：容量不足时调整布局、分面、换实现或如实报未完成，不能改表');
  });
  if (doc.pages.length && !errors.some(e => /缺少合法 page 序号/.test(e))) {
    const numbers = doc.pages.map(p => p.page);
    for (let i = 1; i <= numbers.length; i++) if (!numbers.includes(i)) bad('page 序号不连续：缺少 ' + i);
  }
  errors.push(...repetitionErrors(doc));
  errors.push(...familyDiversityErrors(doc));
  return { status: errors.length ? 'FAIL' : 'PASS', errors, inventory: inventory(doc) };
}

const expression = page => norm(page.visual) || page.form;

/* 一页实际落在哪个编码族：登记形式由 form 决定，svg.custom 由作者声明。 */
function familyExpression(page) {
  if (page && page.form === 'svg.custom') return norm(page.encodingFamily) || 'custom';
  try { return forms.familyOf(page.form); } catch (error) { return 'unknown'; }
}
const familyLabel = family => forms.familyLabels[family] || family;

/* 族分布：不规定用几种、不因数量定级，只要求"塌缩了"和"整族没出现"两件事被明确交代过。
   按名称计数抓不住"七页长度编码分散在五个 form 名下"这种塌缩，所以这一条按族算。 */
function familyTally(doc) {
  const pages = (doc && Array.isArray(doc.pages) ? doc.pages : []).filter(page => page && page.form);
  const counts = {};
  pages.forEach(page => { const family = familyExpression(page); counts[family] = (counts[family] || 0) + 1; });
  const exhibits = pages.filter(page => EXHIBIT_FAMILIES.includes(familyExpression(page)));
  return { counts, exhibits: exhibits.length, total: pages.length };
}

function familyDiversityErrors(doc) {
  const errors = [];
  const { counts, exhibits, total } = familyTally(doc);
  if (!exhibits) return errors;
  const ranked = Object.entries(counts).filter(([family]) => EXHIBIT_FAMILIES.includes(family))
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  const [family, count] = ranked[0] || [];
  if (family && count >= FAMILY_FLOOR && count / exhibits >= FAMILY_SHARE && !norm(doc.familyDiversityReason)) {
    const share = Math.round(count / exhibits * 100);
    errors.push('本稿 ' + exhibits + ' 个展品页中有 ' + count + ' 页（' + share + '%）属「' + familyLabel(family) + '」族，已是最大单族：'
      + '必须在 pages.json 顶层写 familyDiversityReason，说明为什么这些页放不下别的编码族。'
      + '这不是图型配额——不规定用几种，只要求你想过跨族表达并说得出为什么没用。'
      + '若确实有页可以在同一论点上换成别的编码（时间序列、构成、相关、流向、层级等），先换再解释。');
  }
  // 整族缺席也要交代：本案的教训是"有季度数据却没做时间序列"，而缺席在计数表里是看不见的。
  if (exhibits >= UNUSED_REVIEW_FLOOR) {
    const declared = doc.unusedFamilies;
    if (declared === undefined || declared === null) {
      errors.push('本稿有 ' + exhibits + ' 个展品页：必须在 pages.json 顶层写 unusedFamilies，'
        + '逐族说明以下编码族为什么整族没有出现——' + missingFamilies(counts).map(familyLabel).join('、') + '。'
        + '完全没用上是正当结论，但要说得出依据（没有多期序列／没有守恒流量／没有原始观测等）；'
        + '如果只是没想到，那正是这一条要拦的。');
    } else if (typeof declared !== 'object' || Array.isArray(declared)) {
      errors.push('unusedFamilies 须为对象：{ 族: "为什么整族没用上" }');
    } else {
      for (const [key, reason] of Object.entries(declared)) {
        if (!EXHIBIT_FAMILIES.includes(key)) errors.push('unusedFamilies 的键「' + key + '」不是展品族（可用：' + EXHIBIT_FAMILIES.join('/') + '）');
        else if (counts[key]) errors.push('unusedFamilies 声明「' + familyLabel(key) + '」没用上，但本稿已有 ' + counts[key] + ' 页属这一族：要么改这里，要么改那些页的 encodingFamily');
        else if (!norm(reason)) errors.push('unusedFamilies.' + key + ' 的理由不能为空');
      }
      const missing = missingFamilies(counts).filter(key => !(key in declared));
      if (missing.length) errors.push('unusedFamilies 没有覆盖全部缺席族，缺：' + missing.map(familyLabel).join('、'));
    }
  }
  return errors;
}

const missingFamilies = counts => EXHIBIT_FAMILIES.filter(family => !counts[family]);
const exhibitsOf = families => families.filter(([family]) => EXHIBIT_FAMILIES.includes(family)).reduce((sum, [, n]) => sum + n, 0);

/* 重复必须是被解释的决定，不能是默认：同一形式第 3 次起、或连续 3 页同形式，都要写理由。
   这不是图型配额——不规定用几种、不因数量定级，只要求"你注意到了并说得出为什么"。 */
function repetitionErrors(doc) {
  const errors = [], pages = Array.isArray(doc && doc.pages) ? doc.pages : [];
  const counts = {};
  pages.forEach(page => { if (page && page.form) (counts[expression(page)] = counts[expression(page)] || []).push(page); });
  Object.entries(counts).forEach(([form, list]) => {
    list.forEach((page, index) => {
      if (index >= 2 && !norm(page.repetitionReason)) errors.push('page ' + page.page + '：' + form + ' 已是本稿第 ' + (index + 1) + ' 次出现，必须写 repetitionReason 说明为什么这里还是它');
    });
  });
  let run = 1;
  for (let i = 1; i < pages.length; i++) {
    if (pages[i] && pages[i - 1] && pages[i].form && expression(pages[i]) === expression(pages[i - 1])) {
      run += 1;
      if (run >= 3 && !norm(pages[i].repetitionReason)) errors.push('page ' + pages[i].page + '：与前两页同为 ' + expression(pages[i]) + '，连续三页同形式必须写 repetitionReason');
    } else run = 1;
  }
  return [...new Set(errors)];
}

function inventory(doc) {
  const pages = (doc && Array.isArray(doc.pages)) ? doc.pages : [];
  const byForm = {}, byFamily = {}, byVisual = {};
  let annotated = 0, regions = 0;
  const runs = [];
  pages.forEach(page => {
    if (!page || !page.form) return;
    byForm[page.form] = (byForm[page.form] || 0) + 1;
    byVisual[expression(page)] = (byVisual[expression(page)] || 0) + 1;
    const family = familyExpression(page);
    byFamily[family] = (byFamily[family] || 0) + 1;
    if (Array.isArray(page.annotations) && page.annotations.length) annotated += page.annotations.length;
    if (Array.isArray(page.regions)) regions += page.regions.length;
    const last = runs[runs.length - 1];
    if (last && last.form === expression(page)) { last.pages.push(page.page); last.length = last.pages.length; }
    else runs.push({ form: expression(page), pages: [page.page], length: 1 });
  });
  const entries = Object.entries(byForm).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  const families = Object.entries(byFamily).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  const unclassified = byFamily.custom || 0;
  return {
    pages: pages.length,
    forms: Object.fromEntries(entries),
    families: Object.fromEntries(families),
    // 展品页的口径：结构化文字页是兜底、不是编码选择，占比以它为分母会稀释真实的图型集中度。
    exhibits: families.filter(([family]) => EXHIBIT_FAMILIES.includes(family)).reduce((sum, [, n]) => sum + n, 0),
    familyShare: exhibitsOf(families) ? Object.fromEntries(families.map(([family, n]) => [family, Number((n / exhibitsOf(families)).toFixed(3))])) : {},
    largestFamily: (() => { const ranked = families.filter(([family]) => EXHIBIT_FAMILIES.includes(family)); return ranked.length ? { family: ranked[0][0], label: familyLabel(ranked[0][0]), pages: ranked[0][1], share: Number((ranked[0][1] / exhibitsOf(families)).toFixed(3)) } : null; })(),
    absentFamilies: missingFamilies(Object.fromEntries(families)),
    unclassifiedCustom: unclassified,
    distinctForms: entries.length,
    visuals: byVisual,
    distinctVisuals: Object.keys(byVisual).length,
    annotations: annotated,
    regions,
    longestRun: runs.reduce((max, run) => Math.max(max, run.length), 0),
    runs: runs.filter(run => run.length > 1)
  };
}

function load(file) {
  const doc = JSON.parse(fs.readFileSync(file, 'utf8'));
  const result = check(doc);
  if (result.status !== 'PASS') throw new Error('pages 合同无效：' + result.errors.join('；'));
  return { doc, record: path.resolve(file), sha256: fileHash(file), inventory: result.inventory };
}

/* 与成稿对账：页数、顺序与每页声明的 form 必须一一对应；成稿里声明的 data-proves 若存在也必须一致。 */
function verifyDeck(doc, slides) {
  const errors = [];
  const content = slides.filter(slide => !BOOKEND_ROLES.includes(slide.role));
  const pages = (doc && doc.pages) || [];
  if (content.length !== pages.length) errors.push('pages.json 声明 ' + pages.length + ' 页正文，成稿有 ' + content.length + ' 页正文');
  content.forEach((slide, index) => {
    const declared = pages[index];
    if (!declared) { errors.push('第 ' + slide.page + ' 页在 pages.json 中没有对应条目'); return; }
    if (!slide.form) { errors.push('第 ' + slide.page + ' 页缺少 data-form；逐页显式声明，没有静默默认值'); return; }
    try { forms.get(slide.form); } catch (error) { errors.push('第 ' + slide.page + ' 页 ' + error.message); return; }
    if (slide.form !== declared.form) errors.push('第 ' + slide.page + ' 页 data-form="' + slide.form + '" 与 pages.json 的 ' + declared.form + ' 不一致');
    if (declared.visual !== undefined && norm(slide.visual) !== norm(declared.visual)) errors.push('第 ' + slide.page + ' 页 data-visual 缺失或与 pages.json 不一致');
    // 同一句话存在成稿与 pages.json 两处，逐字相同才认。报错要把两句都摊开——
    // 只说"不一致"等于让作者回去逐字比对，页数一多就是纯耗时。
    if (norm(slide.proves) && norm(slide.proves) !== norm(declared.proves)) errors.push('第 ' + slide.page + ' 页 data-proves 与 pages.json 的 proves 不一致：成稿写「' + norm(slide.proves) + '」，pages.json 写「' + norm(declared.proves) + '」；两处必须逐字相同，改完一处要同步另一处');
    // 旁解读对账：声明与成稿必须一一对上。只在作者声明了 annotations 时核对——
    // 由配方在构建期生成、契约里没声明的，不属于本对账范围，但会以成稿实际数量出现在 audit 里。
    if (Array.isArray(slide.annotationIds) && Array.isArray(declared.annotations) && declared.annotations.length) {
      const inDeck = slide.annotationIds.map(norm).filter(Boolean);
      const declaredIds = declared.annotations.map(a => norm(a && a.id)).filter(Boolean);
      const missingInDeck = declaredIds.filter(id => !inDeck.includes(id));
      const undeclared = inDeck.filter(id => !declaredIds.includes(id));
      if (missingInDeck.length) errors.push('第 ' + slide.page + ' 页 pages.json 声明了旁解读 ' + missingInDeck.join('、') + '，但成稿里没有对应的 data-annotation-id：声明了就要真的画出来');
      if (undeclared.length) errors.push('第 ' + slide.page + ' 页成稿有旁解读 ' + undeclared.join('、') + ' 未在 pages.json 声明：补上声明（含 id），否则"这页有没有贴近对象的解读"在交付链上不可核对');
    }
  });
  // 跨页引用：插页、删页或分章调整后，"P19""19 页正文"这类写法最容易悄悄失准。
  // 这类 token 是机械可查的，不该留给人工复核去发现。
  const refs = slides.filter(slide => Array.isArray(slide.pageRefs)).flatMap(slide => slide.pageRefs.map(ref => ({page: slide.page, ref: String(ref)})));
  if (refs.length) {
    for (const {page, ref} of refs) {
      const [kind, raw] = ref.split(':');
      const n = Number(raw);
      if (!Number.isInteger(n)) continue;
      if (kind === 'body' && n !== content.length) errors.push('第 ' + page + ' 页写「' + n + ' 页正文」，实际正文是 ' + content.length + ' 页：插页或删页后这类计数必须同步');
      if (kind === 'p' && (n < 1 || n > content.length)) errors.push('第 ' + page + ' 页引用「P' + n + '」超出正文范围（1–' + content.length + '）');
    }
  }
  return errors;
}

module.exports = {SLOTS, ROLES, BOOKEND_ROLES, ENCODING_FAMILIES, EXHIBIT_FAMILIES, FAMILY_FLOOR, FAMILY_SHARE, UNUSED_REVIEW_FLOOR, check, repetitionErrors, familyDiversityErrors, familyExpression, familyTally, missingFamilies, inventory, load, verifyDeck, fileHash, norm};
