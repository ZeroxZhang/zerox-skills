#!/usr/bin/env node
'use strict';
// 验证门槛反例：不能靠自报支持、错字符或错对象顺序取得视觉通过。
const assert = require('node:assert/strict');
const {verifyImageResponse} = require('./probe_capabilities.cjs');
const key = {code: 'AB2345', shape_left_to_right: ['red square', 'blue circle', 'green triangle']};
const cases = [
  ['中文正确答案', {code: 'AB2345', shape_left_to_right: ['红方块', '蓝圆', '绿三角']}, 'pass'],
  ['结构化正确答案', {code: 'AB2345', shape_left_to_right: [{color:'red',shape:'square'}, {color:'blue',shape:'circle'}, {color:'green',shape:'triangle'}]}, 'pass'],
  ['错误字符', {code: 'AB2346', shape_left_to_right: ['红方块', '蓝圆', '绿三角']}, 'fail'],
  ['对象顺序错误', {code: 'AB2345', shape_left_to_right: ['蓝圆', '红方块', '绿三角']}, 'fail'],
  ['只自报支持', {supported: true, status: 'pass'}, 'fail'],
  ['缺失对象', {code: 'AB2345', shape_left_to_right: ['红方块', '蓝圆']}, 'fail'],
];
for (const [name, response, status] of cases) assert.equal(verifyImageResponse(key, response).status, status, name);
console.log(`PASS ${cases.length} image-answer acceptance/counterexample checks`);
