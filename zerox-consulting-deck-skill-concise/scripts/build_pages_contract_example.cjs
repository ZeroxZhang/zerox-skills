#!/usr/bin/env node
/* 端到端示例：S3 产出 pages.json → 装配逐页对账 → QA 出形式清单 → 交付门禁。
   全部为合成数据，只用于验证链路，不构成任何结论。 */
const fs = require('node:fs'), path = require('node:path'), { execFileSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const kit = require('../assets/exhibit-kit.js');
const themes = require('../assets/deck-themes.js');
const palette = themes.palette('mckinsey');
const profile = 'serif-report-bold';
const build = (type, spec) => kit[type](Object.assign({ palette, typography_id: profile }, spec));
const outDir = path.resolve(process.argv[2] || path.join(root, '..', 'demo', 'pages-contract'));

const exhibit = (title, unit, graphic, note) =>
  '<div class="exhibit"><h2>' + title + '</h2><div class="unit">' + unit + '</div><div class="graphic">' + graphic + '</div>'
  + (note ? '<div class="annotation">' + note + '</div>' : '') + '</div>';

const SOURCE = '来源：本技能合成数据，仅验证页面合同与标注链路，不代表任何真实企业或市场。';
const page = (n, form, proves, title, lead, body) =>
  '<section class="slide reading" data-frame-boundary="integrated" data-form="' + form + '" data-proves="' + proves + '">'
  + '<header class="slide__header"><h1 class="slide__title">' + title + '</h1><div class="slide__lead">' + lead + '</div></header>'
  + '<div class="slide__body">' + body + '</div><div class="source">' + SOURCE + '</div><div class="slide__page">' + n + '</div></section>';

const pagesHtml = [
  page(1, 'kit.dumbbell', '商超是净下滑的主要来源，电商的增长不足以抵消',
    '商超减少 1.1 亿元，电商只抵消了其中约 36%',
    '同一量尺下的两期对比；差额与增长率直接标在对应行旁边。',
    exhibit('01｜渠道规模变化', '亿元；空心＝2024 年，实心＝2025 年',
      build('dumbbell', {
        width: 1160, height: 400, startLabel: '2024年', endLabel: '2025年', format: { decimals: 1 },
        items: [{ label: '商超', start: 6.4, end: 5.3 }, { label: '电商', start: 1.6, end: 2.0 }, { label: '经销', start: 3.2, end: 3.1 }, { label: '直营', start: 0.8, end: 0.9 }],
        annotations: [
          { id: 'd-商超', on: 'end:商超', kind: 'delta', from: 'start:商超', text: '{label} {delta}（{rate}）', weight: 600 },
          { id: 'd-电商', on: 'end:电商', kind: 'delta', from: 'start:电商', text: '{label} {delta}（{rate}）', weight: 600 }
        ]
      }),
      '贡献解释不等于已经识别客户流失的因果；下一步按门店与价格／销量拆解。')),
  page(2, 'kit.mekko', '南区的新业务已是该区主要构成，总量却最小',
    '南区总量最小，但新业务已占该区七成',
    '列宽编码地区总量、段高编码绝对销售额；份额直接标在对应色块旁。',
    exhibit('01｜地区规模 × 产品构成', '合成销售额（任意单位）；列宽＝地区总量，段面积＝绝对销售额',
      build('mekko', {
        width: 1160, height: 400, format: { decimals: 0 }, shareDecimals: 0,
        items: [
          { label: '东区', segments: [{ label: '核心', value: 60 }, { label: '新业务', value: 40 }] },
          { label: '西区', segments: [{ label: '核心', value: 30 }, { label: '新业务', value: 20 }] },
          { label: '南区', segments: [{ label: '核心', value: 30 }, { label: '新业务', value: 70 }] }
        ],
        annotations: [{ id: 'm-南区', on: 'seg:南区|新业务', kind: 'share', text: '{label} 占该区 {value}', weight: 600 }]
      }),
      '同实体跨地区保持同色；窄段放不下名称与数值时改走同侧引线通道，仍按原值画面积。')),
  page(3, 'kit.bullet', '三项指标都没达到目标，交付达成率缺口最大',
    '三项指标均低于目标，缺口最大的是交付达成率',
    '同一指标内实际与目标可比；缺口按真实端点计算，不由减号硬写。',
    exhibit('01｜目标差距', '%；底条为 0–100，粗短线为目标',
      build('bullet', {
        width: 1160, height: 300, format: { decimals: 0 },
        items: [
          { label: '交付达成率%', value: 76, target: 90, max: 100, ranges: [70, 90, 100] },
          { label: '留存率%', value: 68, target: 80, max: 100, ranges: [70, 90, 100] },
          { label: '计划覆盖率%', value: 85, target: 95, max: 100, ranges: [70, 90, 100] }
        ],
        annotations: [
          { id: 'b-交付', on: 'value:交付达成率%', kind: 'delta', from: 'target:交付达成率%', text: '缺口 {delta}', weight: 600 },
          { id: 'b-留存', on: 'value:留存率%', kind: 'delta', from: 'target:留存率%', text: '缺口 {delta}' }
        ]
      }),
      '分档阈值须另有业务定义；指标上升是否更好由业务判断，组件不发明合格线。')),
  page(4, 'kit.waterfall', '净减少 0.8 亿元可直接从贡献桥读出，商超解释主要降幅',
    '净减少 0.8 亿元，商超解释了主要降幅',
    '分项闭合：11.2 + 0.4 − 1.1 − 0.1 = 10.4；贡献标注只陈述会计分解。',
    exhibit('01｜收入变动的贡献分解', '亿元；贡献柱带符号，总计单独表示',
      build('waterfall', {
        width: 1160, height: 400, format: { decimals: 1 },
        items: [
          { label: '期初', type: 'total', value: 11.2 }, { label: '电商', type: 'delta', value: 0.4 },
          { label: '商超', type: 'delta', value: -1.1 }, { label: '经销', type: 'delta', value: -0.1 }, { label: '期末', type: 'subtotal' }
        ],
        annotations: [
          { id: 'w-商超', on: 'bar:商超', kind: 'delta', text: '主要拖累 {value}', weight: 600 },
          { id: 'w-电商', on: 'bar:电商', kind: 'delta', text: '仅抵消拖累的 36%' }
        ]
      }),
      '贡献分解不说明为什么；原因未知时保留在正文限制里。'))
].join('\n');

// S3 的机器可读产物：每页一个 proves 与一个 form。四种形式互不重复，不需要 repetitionReason。
const pagesContract = {
  version: 1,
  pages: [
    { page: 1, proves: '商超是净下滑的主要来源，电商的增长不足以抵消', form: 'kit.dumbbell',
      annotations: [{ on: 'end:商超', kind: 'delta', from: 'start:商超', text: '{label} {delta}（{rate}）' }, { on: 'end:电商', kind: 'delta', from: 'start:电商', text: '{label} {delta}（{rate}）' }] },
    { page: 2, proves: '南区的新业务已是该区主要构成，总量却最小', form: 'kit.mekko',
      annotations: [{ on: 'seg:南区|新业务', kind: 'share', text: '{label} 占该区 {value}' }] },
    { page: 3, proves: '三项指标都没达到目标，交付达成率缺口最大', form: 'kit.bullet',
      annotations: [{ on: 'value:交付达成率%', kind: 'delta', from: 'target:交付达成率%', text: '缺口 {delta}' }, { on: 'value:留存率%', kind: 'delta', from: 'target:留存率%', text: '缺口 {delta}' }] },
    { page: 4, proves: '净减少 0.8 亿元可直接从贡献桥读出，商超解释主要降幅', form: 'kit.waterfall',
      annotations: [{ on: 'bar:商超', kind: 'delta', text: '主要拖累 {value}' }, { on: 'bar:电商', kind: 'delta', text: '仅抵消拖累的 36%' }] }
  ]
};

fs.mkdirSync(outDir, { recursive: true });
const pagesFile = path.join(outDir, 'pages.html'), pagesRecord = path.join(outDir, 'pages.json'), taskFile = path.join(outDir, 'task.json'), deck = path.join(outDir, 'deck.html'), renders = path.join(outDir, 'renders');
fs.writeFileSync(pagesFile, pagesHtml);
fs.writeFileSync(pagesRecord, JSON.stringify(pagesContract, null, 2));
fs.writeFileSync(taskFile, JSON.stringify({
  version: 1, workMode: 'editorial', complexity: 'simple', majorConclusion: false,
  mode: 'reading', theme: 'mckinsey', typography: profile, ratio: '16x9', kind: 'fragment',
  planner: { mode: 'direct' }, pages: { record: 'pages.json' }, critical: []
}, null, 2));

(async () => {
  const report = { outDir, pages: pagesContract.pages.length };
  // 1. 反单调门禁：同一形式第 3 次出现而不解释，必须在装配前就被拒。
  const checkPages = require('./check_pages.cjs');
  const repeated = { version: 1, pages: [1, 2, 3].map(n => ({ page: n, proves: '同一形状连续出现', form: 'kit.bullet' })) };
  const repeatResult = checkPages.check(repeated);
  report.repetitionGate = { status: repeatResult.status, errors: repeatResult.errors };
  if (repeatResult.status !== 'FAIL') throw new Error('反单调门禁未生效');

  // 2. 装配：逐页 data-form 必须与 pages.json 对齐。
  const { assemble } = require('./assemble_deck.cjs');
  report.assembly = await assemble({ pagesFile, outputFile: deck, contractFile: taskFile, title: '渠道复盘 · 页面合同示例' });

  // 3. QA：出形式清单，逐页对账。
  execFileSync(process.execPath, [path.join(__dirname, 'qa_deck.cjs'), deck, renders], { stdio: ['ignore', 'pipe', 'pipe'], maxBuffer: 40 * 1024 * 1024 });
  const audit = JSON.parse(fs.readFileSync(path.join(renders, 'audit.json'), 'utf8'));
  report.qa = { geometryStatus: audit.geometryStatus, errors: audit.errors, pagesCheck: audit.pagesCheck.status, inventory: audit.pagesInventory, annotations: audit.pagesInventory.annotations };

  // 4. 成稿里声明的形式必须与 pages.json 一致（再独立核对一次）。
  report.formsOnPages = audit.rows.map(row => ({ page: row.page, form: row.form, proves: row.proves, exhibits: row.exhibits.length }));

  fs.writeFileSync(path.join(outDir, 'report.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
})().catch(error => { console.error(process.env.STACK ? error.stack : error.message); process.exitCode = 1; });
