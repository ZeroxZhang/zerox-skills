#!/usr/bin/env node
/* 可选本地读取：不依赖实际安装，无解包、缓存或网络。 */
'use strict';
const assert = require('node:assert/strict'), fs = require('node:fs'), os = require('node:os'), path = require('node:path');
const {loadPlanner, collect, describe} = require('./load_viz_planner.cjs');
const temp = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'planner-local-')));
function put(root, name, value) { const p = path.join(root, name); fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,value); }
function fixture(name) {
  const root = path.join(temp,name);
  put(root,'capabilities.json',JSON.stringify({name:'echarts-viz-planner',contract_versions:['1.1'],output_levels:['decision'],echarts_version:'6.1.0',required_files:['references/selection.md']}));
  for (const p of ['SKILL.md','catalog/index.md','references/api-contract.md','references/selection.md','schemas/plan.schema.json','scripts/validate_plan.py']) put(root,p,'fixture');
  return root;
}
try {
  const home=path.join(temp,'empty-home'), options={home,env:{},searchPaths:[]};
  assert.equal(loadPlanner(options).status,'unavailable');
  assert.equal(fs.existsSync(home),false,'查询失败不应创建缓存或安装目录');
  const source=fixture('source'),before=describe(collect(source));
  assert.equal(loadPlanner({...options,planner:source}).source_sha256,before.source_sha256);
  assert.equal(loadPlanner({...options,env:{ECHARTS_VIZ_PLANNER_PATH:source}}).origin,'environment');
  const linked=path.join(temp,'linked');fs.symlinkSync(source,linked,'dir');
  assert.equal(loadPlanner({...options,searchPaths:[linked]}).skill_root,source);
  const bad=fixture('bad');fs.unlinkSync(path.join(bad,'references/selection.md'));
  assert.equal(loadPlanner({...options,planner:bad,searchPaths:[source]}).status,'incompatible','显式来源不可被其他安装静默替换');
  assert.equal(loadPlanner({...options,planner:path.join(temp,'missing'),searchPaths:[source]}).status,'unavailable');
  const drift=fixture('drift');put(drift,'capabilities.json','{}');assert.equal(loadPlanner({...options,planner:drift}).status,'incompatible');
  assert.deepEqual(describe(collect(source)),before,'只读加载不能修改资源');
  put(source,'SKILL.md','changed');assert.notEqual(loadPlanner({...options,planner:source}).source_sha256,before.source_sha256);
  fs.unlinkSync(path.join(source,'SKILL.md'));fs.symlinkSync(path.join(bad,'SKILL.md'),path.join(source,'SKILL.md'));
  assert.equal(loadPlanner({...options,planner:source}).status,'incompatible');
  console.log('PASS local planner: empty environment, no writes, explicit origin, symlink root, incomplete resources, source digest and resource symlink rejection');
} finally {fs.rmSync(temp,{recursive:true,force:true});}
