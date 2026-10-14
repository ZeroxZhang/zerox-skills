/* 配方锚点契约：id 集合、几何有限性、写什么读什么、标注落地、产物可复现、图元分派。
   这里只查生成期查得到的部分；"声明框是否等于真实渲染几何"由 test_annotation_browser.cjs 在真浏览器里查。 */
const assert = require('node:assert/strict');
const { render } = require('./render_echarts_svg.cjs');
const layer = require('../assets/annotation-layer.js');
const examples = require('../assets/recipe-examples.json');
const results = {};

const base = { width: 640, height: 400, theme_id: 'mckinsey', typography_id: 'serif-report-bold' };
const draw = (recipe, extra) => render(Object.assign({ recipe, spec: examples[recipe] }, base, extra));
const ids = plan => plan.anchors.map(a => a.id);
const count = (svg, re) => (svg.match(re) || []).length;

/* 1. 每个配方的锚点 id 集合必须完全相等——不是"包含"：多发一个锚点同样是契约漂移。 */
{
  const expected = {
    rankedBar: ['bar:甲', 'bar:乙'],
    groupedBar: ['bar:甲|本期', 'bar:乙|本期', 'bar:甲|上期', 'bar:乙|上期'],
    timeSeries: ['point:2024|收入', 'point:2025|收入'],
    composition: ['seg:甲|核心', 'seg:甲|新业务'],
    histogram: ['bin:0–10', 'bin:10–20', 'bin:20–30'],
    scatter: ['point:甲', 'point:乙'],
    heatmap: ['cell:市场|规模', 'cell:市场|增长'],
    sankey: ['flow:入口→成交', 'node:入口', 'node:成交'],
    tree: ['node:利润', 'node:收入', 'node:成本']
  };
  const plans = {};
  for (const recipe of Object.keys(expected)) {
    const plan = plans[recipe] = draw(recipe);
    const got = ids(plan);
    assert.equal(new Set(got).size, got.length, recipe + ' 出现重复锚点 id：' + JSON.stringify(got));
    assert.deepEqual([...got].sort(), [...expected[recipe]].sort(), recipe + ' 的锚点 id 集合与约定不符');
  }
  /* 2. 每条锚点的框都必须是 4 个有限数，且中心点落在框内。 */
  for (const [recipe, plan] of Object.entries(plans)) {
    for (const a of plan.anchors) {
      const box = a.box;
      assert.ok(box && [box.x, box.y, box.width, box.height].every(Number.isFinite), recipe + ' 的 ' + a.id + ' 给出非有限框');
      assert.ok(box.width > 0 && box.height > 0, recipe + ' 的 ' + a.id + ' 框为空：' + JSON.stringify(box));
      assert.ok(Math.abs(a.x - (box.x + box.width / 2)) < 1e-6 && Math.abs(a.y - (box.y + box.height / 2)) < 1e-6, recipe + ' 的 ' + a.id + ' 中心点不在框中心');
    }
  }
  results.anchor_ids_match = Object.keys(expected).length;
}

/* 3. 写什么读什么：从序列化后的 SVG 取回的锚点，必须与渲染时声明的一致。
   references/exhibits.md 承诺 collect() 对 ECharts 产物同样可用，这条让它成立。 */
{
  for (const recipe of Object.keys(examples)) {
    const plan = draw(recipe);
    const svg = plan.pages[0].svg;
    assert.equal(count(svg, /data-anchor-id=/g), plan.anchors.length, recipe + ' 的 SVG 锚点数量与声明不符');
    const read = layer.collect(svg);
    assert.deepEqual(Object.keys(read).sort(), ids(plan).sort(), recipe + ' 取回的锚点 id 与声明不符');
    for (const a of plan.anchors) {
      const back = read[a.id];
      assert.ok(Math.abs(back.x - a.x) < .01 && Math.abs(back.y - a.y) < .01, recipe + ' 的 ' + a.id + ' 坐标往返不一致');
      assert.ok(Math.abs(back.box.width - a.box.width) < .01 && Math.abs(back.box.height - a.box.height) < .01, recipe + ' 的 ' + a.id + ' 框往返不一致');
    }
  }
  results.roundtrip = true;
}

/* 4. 声明了标注就必须真的画出来，且引线挂在这张图自己的锚点上。 */
{
  const on = { rankedBar: 'bar:甲', timeSeries: 'point:2024|收入', sankey: 'node:入口', scatter: 'point:甲', tree: 'node:收入' };
  for (const [recipe, target] of Object.entries(on)) {
    const plan = draw(recipe, { padding: 48, annotations: [{ on: target, kind: 'value', text: '读数 {value}' }] });
    const svg = plan.pages[0].svg;
    assert.equal(plan.annotations, 1, recipe + ' 的标注没有落到图上');
    const refs = [...svg.matchAll(/data-anchor-ref="([^"]+)"/g)].map(m => m[1]);
    assert.deepEqual([...new Set(refs)], [target], recipe + ' 的标注没有挂在自己声明的锚点上');
    // 每条标注要么落在图元内，要么带引线在外。
    assert.equal(count(svg, /data-role="leader"/g) + count(svg, /data-placement="inside"/g), count(svg, /data-role="annotation"/g), recipe + ' 的标注既不在图元内也没有引线');
  }
  results.annotations_land = Object.keys(on).length;
}

/* 5. 同一输入必须出同样的字节：成稿哈希要能比对，产物也要能复现。
   zrender 的 zr0-c0 / zr0-g1 / zr0-cls-1 是进程内的实例序号，渲染期已按内容重新编号。 */
{
  for (const recipe of Object.keys(examples)) {
    assert.equal(draw(recipe).pages[0].svg, draw(recipe).pages[0].svg, recipe + ' 两次渲染字节不一致');
  }
  results.reproducible = true;
}

/* 6. 跨图不撞标识：同一篇文档里两张配方图，裁剪/渐变/样式类不能同名。
   同名时 url(#zr0-c0) 会解析到先出现的那个，后一张图会被前一张的裁剪区裁掉。 */
{
  const seen = new Map();
  for (const recipe of Object.keys(examples)) {
    const svg = draw(recipe).pages[0].svg;
    for (const m of svg.matchAll(/\bzr([0-9a-f]{8})-(cls-\d+|c\d+|g\d+)\b/g)) {
      const key = m[1] + '-' + m[2].replace(/\d+$/, '');
      const owner = seen.get(key);
      assert.ok(!owner || owner === recipe, recipe + ' 与 ' + owner + ' 共用标识 ' + key + '，同页会互相覆盖');
      seen.set(key, recipe);
    }
  }
  results.namespaced = seen.size;
}

/* 7. 图元分派：两条数据路径会在同一组 (series, data) 下标上撞车，锚点必须按图元类型分开。
   rankedBar 的基准线画成 ec-line，不是数据图元；桑基节点是 rect、连线是 path。 */
{
  const bars = draw('rankedBar');
  assert.ok(bars.anchors.every(a => a.id.startsWith('bar:')), 'rankedBar 的基准线被当成了数据图元');
  const flow = ids(draw('sankey'));
  assert.ok(flow.includes('node:入口') && flow.includes('flow:入口→成交'), '桑基节点与连线没有按图元类型分开');
  // 基准线换掉不影响锚点：跳过的是图元类型，不是下标。
  const plain = render(Object.assign({ recipe: 'rankedBar', spec: { items: examples.rankedBar.items } }, base));
  assert.deepEqual(ids(plain), ['bar:甲', 'bar:乙'], '没有基准线时锚点集合变了');
  results.element_dispatch = true;
}

/* 8. 退化情形：图元没画出来时要说清是哪根杠杆，不能把人打发去改版式。 */
{
  const periods = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
  const values = [10, 12, 11, 14, 13, 15, 16, 14, 17, 18, 19, 20];
  const long = { periods, series: [{ name: '收入', values }] };
  // 点数一多默认不画数据点：没有图元就没有锚点，这是配方自己的默认。
  assert.equal(render(Object.assign({ recipe: 'timeSeries', spec: long }, base)).anchors.length, 0, '长折线默认不画点时应无锚点');
  // 声明标注时要报出真实原因与杠杆，而不是"放不下"。
  assert.throws(() => render(Object.assign({ recipe: 'timeSeries', spec: long }, base, { annotations: [{ on: 'point:12月|收入', kind: 'value', text: 'x' }] })), /showSymbol/, '长折线落空时未点出 showSymbol 这根杠杆');
  // 显式开关能把点画出来，锚点随之回来。
  assert.equal(render(Object.assign({ recipe: 'timeSeries', spec: Object.assign({ showSymbol: true }, long) }, base)).anchors.length, 12, 'showSymbol:true 没有把点画出来');
  // 空值点没有图元，就不该有锚点，也不该被编成 0。
  const gap = render(Object.assign({ recipe: 'timeSeries', spec: { periods: ['2024', '2025', '2026'], series: [{ name: '收入', values: [10, null, 12] }] } }, base));
  assert.deepEqual(gap.anchors.map(a => a.value), [10, 12], '空值点被编出了锚点值');
  // id 写错时列出本图可用的锚点，而不是让人去改版式。
  assert.throws(() => draw('histogram', { annotations: [{ on: 'bin:不存在', kind: 'value', text: 'x' }] }), /本图可用的锚点：bin:0–10/, '写错 id 时没有列出可用锚点');
  results.degenerate = true;
}

/* 9. 散点锚点的原值只取纵轴：data-anchor-value 只有一个字段，横轴与规模留在标签上。 */
{
  const plan = draw('scatter');
  const byId = Object.fromEntries(plan.anchors.map(a => [a.id, a]));
  assert.equal(byId['point:甲'].value, 2, '散点锚点原值没取纵轴');
  assert.equal(byId['point:乙'].value, 1, '散点锚点原值没取纵轴');
  results.scatter_value_is_y = true;
}

console.log(JSON.stringify({ pass: true, recipes: Object.keys(examples).length, ...results }));
