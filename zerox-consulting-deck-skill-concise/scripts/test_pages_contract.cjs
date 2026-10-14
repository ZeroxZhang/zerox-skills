/* pages 合同：结构、封闭枚举、成稿对账，以及"枚举里的每条形式都真的存在"。不依赖浏览器。 */
const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), os = require('node:os');
const C = require('./check_pages.cjs');
const forms = require('../assets/deck-forms.js');
const kit = require('../assets/exhibit-kit.js');
const recipes = require('../assets/echarts-recipes.js');
const precision = require('./render_precision_exhibit.cjs');
const diagram = require('./render_diagram.cjs');
const recipeRender = require('./render_echarts_svg.cjs').render;
const palette = require('../assets/deck-themes.js').palette('mckinsey');
const results = {};

const page = (over = {}) => Object.assign({ page: 1, proves: '本页要让读者看出的关系', form: 'html.text' }, over);

// 1. 枚举自身必须完整：每个 form 有族、标签、画法、容量。
for (const form of forms.list()) {
  const entry = forms.get(form);
  assert.ok(entry.family && forms.familyLabels[entry.family], form + ' 缺少已登记的分析族');
  assert.ok(entry.label && entry.capacity, form + ' 缺少标签或容量边界');
  assert.ok(['svg', 'html'].includes(entry.kind), form + ' kind 须为 svg/html');
  assert.ok([null, 'layer', 'comparisons'].includes(entry.annotation), form + ' annotation 入口无效');
}
results.enum_complete = forms.list().length;

// 2. 枚举必须与真实实现一一对应，不能登记渲染不出来的名字。
for (const form of forms.list()) {
  const entry = forms.get(form);
  if (entry.module === 'exhibit-kit') assert.equal(typeof kit[entry.export], 'function', form + ' 在 exhibit-kit 中不存在');
  else if (entry.module === 'echarts-recipes') assert.equal(typeof recipes[entry.export], 'function', form + ' 在 echarts-recipes 中不存在');
  else if (entry.module === 'diagram') { assert.equal(typeof diagram.layout, 'function'); assert.equal(typeof diagram.render, 'function'); }
  else if (entry.module === 'precision') {
    const sample = entry.type === 'stacked'
      ? [{ id: 'a', label: '列', segments: [{ id: 's', label: '段', value: 10 }] }]
      : entry.type === 'waterfall'
        ? [{ id: 'a', label: '起点', type: 'total', value: 10 }, { id: 'b', label: '变化', type: 'delta', value: -3 }, { id: 'c', label: '期末', type: 'total', value: 7 }]
        : [{ id: 'a', label: '项', value: 10 }, { id: 'b', label: '项二', value: 4 }];
    assert.doesNotThrow(() => precision.normalize({ type: entry.type, items: sample, width: 400, height: 260 }), form + ' 的 type 未被精度入口接受');
  }
}
results.enum_matches_implementation = true;

// 3. annotation='layer' 的形式必须真的能出引线标注，不能只是声明。
const annotated = [];
const base = { palette, typography_id: 'serif-report-bold', width: 720, height: 400 };
// 配方样例：与 test_echarts_recipes.cjs 同一组，保证测的是真实可跑的输入。
const cases = {
  rankedBar: { items: [{ label: '乙', value: 2 }, { label: '甲', value: 5 }], baseline: 3 },
  groupedBar: { categories: ['甲', '乙'], series: [{ name: '本期', values: [8, -2] }, { name: '上期', values: [6, 1] }] },
  timeSeries: { periods: ['2024', '2025'], series: [{ name: '收入', values: [10, 12] }] },
  composition: { mode: 'percent', items: [{ label: '甲', segments: [{ label: '核心', value: 80 }, { label: '新业务', value: 20 }] }] },
  histogram: { bins: [{ label: '0–10', value: 3 }, { label: '10–20', value: 7 }, { label: '20–30', value: 2 }] },
  scatter: { items: [{ label: '甲', x: 1, y: 2, size: 100 }, { label: '乙', x: 2, y: 1, size: 25 }] },
  heatmap: { rows: ['市场'], columns: ['规模', '增长'], values: [[4, 5]], min: 1, max: 5 },
  sankey: { nodes: ['入口', '成交'], links: [{ source: '入口', target: '成交', value: 8 }] },
  tree: { root: { label: '利润', value: 888, children: [{ label: '收入', value: 999 }, { label: '成本', value: 111 }] } }
};
const kitCases = {
  'kit.waterfall': ['waterfall', { items: [{ label: '期初', type: 'total', value: 10 }, { label: '变化', type: 'delta', value: -3 }, { label: '期末', type: 'total', value: 7 }], annotations: [{ on: 'bar:变化', kind: 'delta', text: '主要拖累 {value}' }] }],
  'kit.dumbbell': ['dumbbell', { items: [{ label: '甲', start: 6, end: 5 }, { label: '乙', start: 2, end: 3 }], annotations: [{ on: 'end:甲', kind: 'delta', from: 'start:甲', text: '{label} {delta}（{rate}）' }] }],
  'kit.slope': ['slope', { items: [{ label: '甲', start: 6, end: 5 }, { label: '乙', start: 2, end: 3 }], annotations: [{ on: 'end:乙', kind: 'delta', from: 'start:乙' }] }],
  'kit.bullet': ['bullet', { items: [{ label: '达成率%', value: 76, target: 90, max: 100 }], annotations: [{ on: 'value:达成率%', kind: 'delta', from: 'target:达成率%', text: '缺口 {delta}' }] }],
  'kit.heatmap': ['heatmap', { rows: ['北区', '南区'], columns: ['Q1', 'Q2', 'Q3'], values: [[88, 91, 76], [64, 70, 78]], domain: [60, 100], annotations: [{ on: 'cell:北区|Q2', kind: 'value', text: '最高 {value}' }] }],
  'kit.mekko': ['mekko', { items: [{ label: '东区', segments: [{ label: '核心', value: 60 }, { label: '新业务', value: 40 }] }, { label: '南区', segments: [{ label: '核心', value: 30 }, { label: '新业务', value: 70 }] }], annotations: [{ on: 'seg:南区|新业务', kind: 'share', text: '{label} 占该区 {value}' }] }],
  'kit.stacked': ['stacked', { items: [{ label: '东区', segments: [{ label: '核心', value: 60 }, { label: '新业务', value: 40 }] }, { label: '南区', segments: [{ label: '核心', value: 30 }, { label: '新业务', value: 70 }] }], annotations: [{ on: 'seg:东区|核心', kind: 'share', text: '{label} {value}' }] }]
};
// 配方走 ECharts 出图 + 标注层：锚点 id 由配方自己定义，这里逐条点名，顺带把 id 约定钉进测试。
const recipeCases = {
  'recipe.rankedBar': [cases.rankedBar, 'bar:甲'],
  'recipe.groupedBar': [cases.groupedBar, 'bar:甲|本期'],
  'recipe.timeSeries': [cases.timeSeries, 'point:2024|收入'],
  'recipe.composition': [cases.composition, 'seg:甲|核心'],
  'recipe.histogram': [cases.histogram, 'bin:0–10'],
  'recipe.scatter': [cases.scatter, 'point:甲'],
  'recipe.heatmap': [cases.heatmap, 'cell:市场|规模'],
  'recipe.sankey': [cases.sankey, 'node:入口'],
  'recipe.tree': [cases.tree, 'node:利润']
};
for (const form of forms.list().filter(f => forms.annotationEntry(f) === 'layer')) {
  if (kitCases[form]) {
    const [fn, spec] = kitCases[form];
    const svg = kit[fn](Object.assign({}, base, spec));
    assert.match(svg, /data-role="annotation"/, form + ' 声明可标注却没有输出标注文字');
    assert.match(svg, /data-role="leader"/, form + ' 外置标注必须带引线');
    assert.match(svg, /data-requested-size="\d+×\d+" data-actual-size="\d+×\d+"/, form + ' 缺少 requested/actual 尺寸回传');
    assert.match(svg, /data-anchor-id=/, form + ' 缺少统一锚点契约');
  } else if (recipeCases[form]) {
    const [spec, on] = recipeCases[form];
    const plan = recipeRender({ recipe: forms.get(form).export, spec, width: 720, height: 400, padding: 48, theme_id: 'mckinsey', typography_id: 'serif-report-bold', annotations: [{ on, kind: 'value', text: '读数 {value}' }] });
    const svg = plan.pages[0].svg;
    assert.equal(plan.annotations, 1, form + ' 声明的标注没有落到图上');
    assert.match(svg, /data-role="annotation"/, form + ' 声明可标注却没有输出标注文字');
    // 配方图有实心图元，标注可能落在图元内（此时本就不该有引线）；外置的必须带引线。
    const count = re => (svg.match(re) || []).length;
    assert.equal(count(/data-role="leader"/g) + count(/data-placement="inside"/g), count(/data-role="annotation"/g), form + ' 的标注既不在图元内也没有引线');
    assert.match(svg, /data-requested-size="\d+×\d+" data-actual-size="\d+×\d+"/, form + ' 缺少 requested/actual 尺寸回传');
    assert.match(svg, /data-anchor-id=/, form + ' 缺少统一锚点契约');
  } else {
    const entry = forms.get(form);
    const items = entry.type === 'stacked'
      ? [{ id: 'a', label: '列', segments: [{ id: 's1', label: '段一', value: 30 }, { id: 's2', label: '段二', value: 20 }] }]
      : entry.type === 'waterfall'
        ? [{ id: 'a', label: '起点', type: 'total', value: 10 }, { id: 'b', label: '变化', type: 'delta', value: -3 }, { id: 'c', label: '期末', type: 'total', value: 7 }]
        : [{ id: 'a', label: '甲', value: 42 }, { id: 'b', label: '乙', value: 31 }];
    const target = entry.type === 'stacked' ? 'a::s2' : entry.type === 'waterfall' ? 'b' : 'b';
    const svg = precision.render({ type: entry.type, width: 720, height: 400, items, annotations: [{ on: target, kind: 'value', text: '读数 {value}' }] });
    assert.match(svg, /data-role="annotation"/, form + ' 声明可标注却没有输出标注文字');
    assert.match(svg, /data-anchor-id=/, form + ' 缺少统一锚点契约');
  }
  annotated.push(form);
}
results.annotation_entries_work = annotated.length;

// 4. 未接入标注层的形式不能静默接受，但也不再一律拒绝：声明手摆即可写，责任转到目视验收。
//    一律拒绝会把作者逼回少数可标注形式，反而压低编码族多样性。
{
  const silent = C.check({ version: 1, pages: [page({ form: 'kit.tree', annotations: [{ id: 'x1', on: 'x', kind: 'value' }] })] });
  assert.equal(silent.status, 'FAIL', '不声明就是一个静默默认，必须拦住');
  assert.ok(silent.errors.some(e => /未接入通用标注层/.test(e) && /annotationMode/.test(e)), JSON.stringify(silent.errors));
  const declared = C.check({ version: 1, pages: [page({ form: 'kit.tree', annotationMode: 'manual', annotations: [{ id: 'x1', on: 'x', kind: 'value' }] })] });
  assert.equal(declared.status, 'PASS', JSON.stringify(declared.errors));
  const compared = C.check({ version: 1, pages: [page({ form: 'kit.bullet', annotations: [{ id: 'x1', on: 'x', kind: 'value' }] })] });
  assert.equal(compared.status, 'PASS', '接入通用层的形式照常直接写');
  results.annotation_admission_explicit = true;
}

// 5. 结构与语义校验。
{
  assert.equal(C.check({ version: 1, pages: [page()] }).status, 'PASS');
  const cases = [
    [{ version: 2, pages: [page()] }, /version/],
    [{ version: 1, pages: [] }, /非空数组/],
    [{ version: 1, pages: [page({ proves: '  ' })] }, /缺少 proves/],
    [{ version: 1, pages: [page({ form: 'kit.donut' })] }, /未知图示形式/],
    [{ version: 1, pages: [page({ page: 1 }), page({ page: 1 })] }, /序号重复/],
    [{ version: 1, pages: [page({ page: 2 })] }, /不连续/],
    [{ version: 1, pages: [page({ form: 'kit.bullet', annotations: [{ id: 'n1', on: 'a', kind: 'note' }] })] }, /必须给 text/],
    [{ version: 1, pages: [page({ form: 'kit.bullet', annotations: [{ id: 'b1', on: 'a', kind: 'bracket' }] })] }, /必须给 from/],
    [{ version: 1, pages: [page({ form: 'kit.bullet', annotations: [{ id: 'x1', on: 'a', kind: 'nope' }] })] }, /kind 须为/],
    [{ version: 1, pages: [page({ form: 'kit.bullet', annotations: [{ id: 'v1', kind: 'value' }] })] }, /缺少 on/],
    [{ version: 1, pages: [page({ regions: [{ slot: 'left', span: 5, form: 'kit.mekko', role: 'support' }] })] }, /恰好有一个 role="primary"/],
    [{ version: 1, pages: [page({ regions: [{ slot: 'left', span: 5, form: 'kit.mekko', role: 'primary' }] })] }, /主区形式与 page.form 不一致/],
    [{ version: 1, pages: [page({ fallback: { if: '容量不足' } })] }, /fallback/]
  ];
  for (const [doc, pattern] of cases) { const out = C.check(doc); assert.equal(out.status, 'FAIL'); assert.ok(out.errors.some(e => pattern.test(e)), JSON.stringify(doc) + ' → ' + JSON.stringify(out.errors)); }
  results.schema_negatives = cases.length;
}

// 6. 反单调：同一形式第 3 次起、连续 3 页同形式，都必须写理由；这不是图型配额。
{
  const three = [page({ page: 1, form: 'kit.bullet' }), page({ page: 2, form: 'kit.bullet' }), page({ page: 3, form: 'kit.bullet' })];
  const out = C.check({ version: 1, pages: three });
  assert.equal(out.status, 'FAIL');
  assert.ok(out.errors.some(e => /第 3 次出现/.test(e)));
  assert.ok(out.errors.some(e => /连续三页同形式/.test(e)));
  const explained = C.check({ version: 1, pages: [three[0], three[1], page({ page: 3, form: 'kit.bullet', repetitionReason: '三张卡片本就是同一指标的分组复核' })] });
  assert.equal(explained.status, 'PASS', JSON.stringify(explained.errors));
  const twice = C.check({ version: 1, pages: [page({ page: 1, form: 'kit.bullet' }), page({ page: 2, form: 'kit.bullet' })] });
  assert.equal(twice.status, 'PASS', '只重复两次不强制解释，避免变成配额');
  results.repetition_gate = true;
}

// 7. 形式清单：计数、族分布、连续段。
{
  const inv = C.inventory({ version: 1, pages: [page({ page: 1, form: 'kit.dumbbell' }), page({ page: 2, form: 'kit.mekko' }), page({ page: 3, form: 'kit.mekko' }), page({ page: 4, form: 'kit.bullet' })] });
  assert.deepEqual(inv.forms, { 'kit.mekko': 2, 'kit.dumbbell': 1, 'kit.bullet': 1 });
  assert.equal(inv.families.composition, 2);
  assert.equal(inv.distinctForms, 3);
  assert.equal(inv.longestRun, 2);
  assert.deepEqual(inv.runs, [{ form: 'kit.mekko', pages: [2, 3], length: 2 }]);
  results.inventory = true;
}

// 7b. 族分布：按编码族计数，并强制交代整族缺席——两条都是按名计数抓不到的。
{
  // 七页长度编码散在五个 form 名下：按名一次都不触发，按族却是最大单族。这正是 09-18 跑批的形态。
  const collapse = { version: 1, pages: [
    page({ page: 1, form: 'recipe.rankedBar' }), page({ page: 2, form: 'recipe.rankedBar' }),
    page({ page: 3, form: 'recipe.groupedBar' }), page({ page: 4, form: 'recipe.groupedBar' }),
    page({ page: 5, form: 'kit.dumbbell' }), page({ page: 6, form: 'kit.waterfall' }),
    page({ page: 7, form: 'kit.slope' }),
    page({ page: 8, form: 'html.text' }), page({ page: 9, form: 'html.table' }),
    page({ page: 10, form: 'kit.stacked' })
  ] };
  assert.equal(C.repetitionErrors(collapse).length, 0, '按名计数对分散命名确实一次都不触发——这正是它失效的原因');
  const out = C.check(collapse);
  assert.equal(out.status, 'FAIL');
  assert.ok(out.errors.some(e => /最大单族/.test(e) && /familyDiversityReason/.test(e)), JSON.stringify(out.errors));
  // 占比以展品页为分母：那一页结构化文字是兜底，不参与稀释。
  assert.equal(out.inventory.exhibits, 9);
  assert.equal(out.inventory.largestFamily.family, 'comparison');
  assert.equal(out.inventory.largestFamily.pages, 7);
  assert.equal(out.inventory.largestFamily.share, 0.778);
  assert.ok(out.errors.some(e => /unusedFamilies/.test(e)), '整族缺席必须被交代');
  assert.deepEqual(out.inventory.absentFamilies, ['trend', 'distribution', 'correlation', 'flow', 'hierarchy', 'kpi', 'diagram']);
  // 只补族集中度的理由还不够：缺席族那条仍然要答。
  const half = { ...collapse, familyDiversityReason: '本稿主线是同一批对象在同一量尺上的排序变迁，七页共用长度编码' };
  assert.ok(C.check(half).errors.some(e => /unusedFamilies/.test(e)));
  const reasons = Object.fromEntries(out.inventory.absentFamilies.map((f, i) => [f, '材料里没有支撑这一族的' + ['多期序列', '原始观测', '两变量配对', '守恒流量', '层级拆分', '目标线', '机制边'][i] || '依据']));
  const explained = { ...half, unusedFamilies: reasons };
  assert.equal(C.check(explained).status, 'PASS', JSON.stringify(C.check(explained).errors));
  // 理由不许与事实打架：声明某族没用上，但稿子里明明有。
  assert.ok(C.check({ ...explained, unusedFamilies: { ...reasons, table: '没有逐格查数需求' } }).errors.some(e => /已有 1 页属这一族/.test(e)));
  // 缺席族没列全也要拦。
  const partial = { ...reasons }; delete partial.trend;
  assert.ok(C.check({ ...half, unusedFamilies: partial }).errors.some(e => /没有覆盖全部缺席族/.test(e)));
  // 小稿不触发：两个下限一起把它挡在外面，避免把规则变成配额。
  const small = { version: 1, pages: [page({ page: 1, form: 'kit.bullet' }), page({ page: 2, form: 'kit.bullet', repetitionReason: '同一指标的分组复核' }), page({ page: 3, form: 'kit.bullet', repetitionReason: '同一指标的分组复核' })] };
  assert.equal(C.check(small).errors.some(e => /最大单族|unusedFamilies/.test(e)), false, JSON.stringify(C.check(small).errors));
  // 展品只有 7 页时不到缺席族的下限，最大族 3 页也不到集中度下限。
  const wide = { version: 1, pages: Array.from({ length: 40 }, (_, i) => page({ page: i + 1, form: i < 3 ? 'recipe.rankedBar' : ['kit.mekko', 'kit.heatmap', 'recipe.timeSeries', 'html.table'][i - 3] || 'html.text' })) };
  assert.equal(C.check(wide).errors.some(e => /最大单族|unusedFamilies/.test(e)), false, JSON.stringify(C.check(wide).errors));
  results.family_diversity = true;
}

// 7c. 未登记入口必须自报编码族，否则族分布对 svg.custom 全部失明。
{
  assert.equal(C.check({ version: 1, pages: [page({ form: 'svg.custom', visual: 'ecdf' })] }).errors.some(e => /encodingFamily/.test(e)), true);
  assert.equal(C.check({ version: 1, pages: [page({ form: 'svg.custom', visual: 'ecdf', encodingFamily: 'custom' })] }).errors.some(e => /自定义族|未登记/.test(e)), true);
  assert.equal(C.check({ version: 1, pages: [page({ form: 'svg.custom', visual: 'ecdf', encodingFamily: 'distribution' })] }).status, 'PASS');
  assert.equal(C.check({ version: 1, pages: [page({ form: 'kit.mekko', encodingFamily: 'distribution' })] }).errors.some(e => /只用于 svg.custom/.test(e)), true);
  results.encoding_family_declared = true;
}

// 7d. 标注准入：不再按形式族拒绝，改按"谁负责摆位"。
{
  const manual = { version: 1, pages: [page({ form: 'html.table', annotationMode: 'manual', annotations: [{ id: 'a1', on: 'a1', kind: 'note', text: '合计口径见 P22' }] })] };
  assert.equal(C.check(manual).status, 'PASS', JSON.stringify(C.check(manual).errors));
  assert.equal(C.check({ version: 1, pages: [page({ form: 'html.table', annotations: [{ id: 'a1', on: 'a1', kind: 'note', text: 'x' }] })] }).errors.some(e => /annotationMode/.test(e)), true, '手摆必须显式声明，不能默认');
  assert.equal(C.check({ version: 1, pages: [page({ form: 'kit.bullet', annotationMode: 'manual', annotations: [{ id: 'a1', on: 'a1', kind: 'note', text: 'x' }] })] }).errors.some(e => /已接入通用标注层/.test(e)), true, '自动摆位的形式不该声明手摆');
  results.annotation_admission = true;
}

// 8. 与成稿对账：页数、顺序、逐页 form，以及可选的 data-proves。
{
  const doc = { version: 1, pages: [page({ page: 1, form: 'kit.dumbbell', proves: '甲下降最多' }), page({ page: 2, form: 'html.text', proves: '边界说明' })] };
  const slides = [{ page: 1, form: 'kit.dumbbell', proves: '甲下降最多', role: null }, { page: 2, form: 'html.text', proves: '边界说明', role: null }];
  assert.deepEqual(C.verifyDeck(doc, slides), []);
  assert.ok(C.verifyDeck(doc, slides.slice(0, 1)).some(e => /成稿有 1 页正文/.test(e)));
  assert.ok(C.verifyDeck(doc, [slides[0], { ...slides[1], form: null }]).some(e => /缺少 data-form/.test(e)));
  assert.ok(C.verifyDeck(doc, [slides[0], { ...slides[1], form: 'html.table' }]).some(e => /不一致/.test(e)));
  assert.ok(C.verifyDeck(doc, [slides[0], { ...slides[1], proves: '别的说法' }]).some(e => /data-proves/.test(e)));
  assert.deepEqual(C.verifyDeck(doc, [...slides, { page: 3, form: null, proves: '', role: 'cover' }]), [], '封面不承担证明责任，不参与对账');
  results.deck_reconciliation = true;
}

// 8b. 成稿对账的扩展：旁解读要真的画出来，跨页引用要跟着页序走。
//     这两类过去都没有对账入口——声明写了没人查，页序一动引用就悄悄失准。
{
  const doc = { version: 1, pages: [
    page({ page: 1, form: 'kit.bullet', annotations: [{ id: 'a1', on: 'value:甲', kind: 'value' }] }),
    page({ page: 2, form: 'html.text' })
  ] };
  const base = [{ page: 1, form: 'kit.bullet', proves: '本页要让读者看出的关系', role: null, annotationIds: ['a1'] },
    { page: 2, form: 'html.text', proves: '本页要让读者看出的关系', role: null }];
  assert.deepEqual(C.verifyDeck(doc, base), []);
  assert.ok(C.verifyDeck(doc, [{ ...base[0], annotationIds: [] }, base[1]]).some(e => /声明了旁解读 a1/.test(e)), '声明了却没画出来');
  assert.ok(C.verifyDeck(doc, [{ ...base[0], annotationIds: ['a1', 'a9'] }, base[1]]).some(e => /未在 pages.json 声明/.test(e)), '画了却没声明');
  const refs = [{ ...base[0], pageRefs: ['body:3'] }, { ...base[1], pageRefs: ['p:7'] }];
  const out = C.verifyDeck(doc, refs);
  assert.ok(out.some(e => /写「3 页正文」，实际正文是 2 页/.test(e)), JSON.stringify(out));
  assert.ok(out.some(e => /引用「P7」超出正文范围/.test(e)), JSON.stringify(out));
  assert.deepEqual(C.verifyDeck(doc, [{ ...base[0], pageRefs: ['body:2'] }, { ...base[1], pageRefs: ['p:1'] }]), [], '对得上就不报');
  results.deck_reconciliation_extended = true;
}

// 9. 文件往返与摘要绑定。
{
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'pages-contract-'));
  try {
    const file = path.join(dir, 'pages.json');
    fs.writeFileSync(file, JSON.stringify({ version: 1, pages: [page({ form: 'kit.bullet' })] }));
    const loaded = C.load(file);
    assert.equal(loaded.sha256, C.fileHash(file));
    assert.equal(loaded.inventory.pages, 1);
    fs.writeFileSync(file, JSON.stringify({ version: 1, pages: [page({ form: 'kit.donut' })] }));
    assert.throws(() => C.load(file), /未知图示形式/);
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
  results.roundtrip = true;
}

// 10. 随包样稿必须示范当前契约，不能停留在旧做法上。
{
  for (const name of ['reference_deck', 'analysis_reference_deck']) {
    const html = path.join(__dirname, '..', 'assets', name + '.html');
    const record = path.join(__dirname, '..', 'assets', name + '.pages.json');
    if (!fs.existsSync(html)) continue;
    assert.ok(fs.existsSync(record), name + ' 缺少随附的 pages.json：样稿必须示范当前契约');
    const doc = JSON.parse(fs.readFileSync(record, 'utf8'));
    const checked = C.check(doc);
    assert.equal(checked.status, 'PASS', name + ' 的 pages.json 不合法：' + JSON.stringify(checked.errors));
    const declared = [...fs.readFileSync(html, 'utf8').matchAll(/data-form="([^"]+)"/g)].map(m => m[1]);
    assert.deepEqual(declared, doc.pages.map(p => p.form), name + ' 的 data-form 与 pages.json 顺序不一致');
    for (const form of declared) assert.doesNotThrow(() => forms.get(form), name + ' 声明了未知形式 ' + form);
  }
  results.samples_follow_contract = true;
}

// 11. 查实现入口不能触发外部 planner；空安装环境照样得到完整本地清单。
{
  const sweep = require('./sweep_forms.cjs').sweep();
  assert.equal(sweep.families.reduce((n, group) => n + group.forms.length, 0), forms.list().length);
  assert.equal(require.cache[require.resolve('./load_viz_planner.cjs')], undefined, '本地入口查询不应加载 planner');
  results.local_sweep = true;
}

// 12. 三种自定义图不算重复，同种图换实现入口仍算重复；不能由能力映射挡住真实 SVG 实现。
{
  const custom = (pageNumber, visual, extra = {}) => page({ page: pageNumber, form: 'svg.custom', visual, encodingFamily: 'correlation', ...extra });
  const mixed = { version: 1, pages: [custom(1, 'ecdf'), custom(2, 'forest'), custom(3, 'adjacency-matrix', { planner: { capability_id: 'heatmap.matrix' } })] };
  assert.equal(C.check(mixed).status, 'PASS');
  assert.equal(C.inventory(mixed).distinctVisuals, 3);
  assert.equal(C.inventory(mixed).longestRun, 1);
  // svg.custom 按声明的 encodingFamily 记账；记成 custom 的话族分布就对这一族失明。
  assert.equal(C.inventory(mixed).families.correlation, 3);
  assert.equal(C.inventory(mixed).unclassifiedCustom, 0);
  // 同一种表达，三种实现入口：已登记形式的族由 form 决定，不该再带 encodingFamily。
  const repeated = { version: 1, pages: [custom(1, 'waterfall'),
    page({ page: 2, form: 'kit.waterfall', visual: 'waterfall' }),
    page({ page: 3, form: 'precision.waterfall', visual: 'waterfall' })] };
  assert.equal(C.check(repeated).status, 'FAIL');
  repeated.pages[2].repetitionReason = '三个业务单元统一量尺核对同一种贡献分解';
  assert.equal(C.check(repeated).status, 'PASS');
  assert.equal(C.check({version:1,pages:[custom(1, '')]}).status, 'FAIL');
  assert.equal(C.check({version:1,pages:[page({form:'svg.custom'})]}).status, 'FAIL');
  assert.equal(C.check({version:1,pages:[custom(1,'forest',{regions:[{slot:'main',role:'primary',span:12,form:'svg.custom'}]})]}).status, 'FAIL');
  assert.equal(C.check({version:1,pages:[custom(1,'forest',{regions:[{slot:'main',role:'primary',span:12,form:'svg.custom',visual:'bar'}]})]}).status, 'FAIL');
  const actual = mixed.pages.map(p => ({...p, role:null}));
  assert.deepEqual(C.verifyDeck(mixed, actual), []);
  assert.ok(C.verifyDeck(mixed, actual.map(p=>({...p, visual:''}))).every(e=>e.includes('data-visual')));
  assert.ok(C.verifyDeck(mixed, [{...actual[0],visual:'bar'},...actual.slice(1)]).some(e=>e.includes('data-visual')));
  results.open_visuals = true;
}
console.log(JSON.stringify({ pass: true, forms: forms.list().length, ...results }));
