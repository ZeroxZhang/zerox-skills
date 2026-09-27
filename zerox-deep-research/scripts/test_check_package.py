#!/usr/bin/env python3
"""文件级回归：覆盖旧包漏检、数据血缘、封包失败与内容变更。临时包自动清理。"""
import contextlib
import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import check_package as checker

SCRIPT_DIR = Path(__file__).resolve().parent


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pkg = Path(self.tmp.name) / 'research'
        self.pkg.mkdir()
        self.config = dict(schema_version=2, package_id='test-revenue', topic='测试用虚构收入',
                           information_cutoff='2026-09-27', data_status='available', data_reason='验证收入及增速',
                           search_status='not_applicable', search_reason='只用给定的虚构测试材料')
        self.json('package.json', self.config)
        for rel, content in {
            'work/brief.md': '比较虚构公司两年收入与增速；保留数据。',
            'work/plan.md': '研究和核验完成；封包状态以 qa 为准。',
            'README.md': '# 测试包\n' + checker.STAT_START + '\n待生成\n' + checker.STAT_END,
            'data/README.md': '这是仅用于回归的虚构数据。按记录 ID 追溯。',
            'raw/files/M001-input.txt': '2024 年收入 100 百万元。2025 年收入 125 百万元。',
            'analysis/growth.md': 'G1 = (R2 / R1 - 1) * 100 = 25，单位 percent；两年均为 CNY 百万元。',
            'notes/M-revenue.md': '## E-001 收入\n\n- 论断: 收入提高\n- 来源: `M001` · 定位: 第 1 段\n- 逐字摘录:\n\n  > 2024 年收入 100 百万元。2025 年收入 125 百万元。\n\n- 解读: 同口径增长\n',
            'report.md': '# 测试报告\n\n收入增长 25%。[1] [数据:G1](data/curated/growth.csv)\n\n## 参考来源\n\n- [1] 测试材料. 来源 ID `M001` 存档 [原文](raw/sources/M001-input.md)\n',
            'sources.md': '| ID | 标题 | 作者/机构 | 发布 | 访问 | 层级 | 可信度 | 完整度 | 采集方式 | 本地文件 | URL | 引用号 | 备注 |\n| M001 | 测试 | 作者 | unknown | 2026 | 一手 | A | full | script | raw/sources/M001-input.md | file:input | [1] | 测试 |\n',
        }.items():
            self.write(rel, content)
        self.meta = {k: 'none' for k in checker.REQUIRED_META}
        self.meta.update(id='M001', title='测试', url='file:input', final_url='file:input',
                         source_type='primary', credibility='A', capture_method='script', completeness='full',
                         original_files=['raw/files/M001-input.txt'], sha256=checker.sha256_of(self.pkg/'raw/files/M001-input.txt'),
                         supersedes=None, archive_url=None)
        self.snapshot()
        base = dict(record_id='R1', entity='虚构公司', metric='revenue', value='100', value_type='number',
                    unit='million CNY', period='2024', geography='global', scope='合并营收', value_origin='reported',
                    status='present', source_id='M001', source_locator='第1段', original_value='100 百万元',
                    input_ids='', method='', missing_reason='')
        self.extracted = [base, dict(base, record_id='R2', period='2025', value='125', original_value='125 百万元')]
        self.curated = [dict(base, record_id='G1', metric='growth', value='25', unit='percent', period='2024-2025',
                             value_origin='derived', source_id='', source_locator='', original_value='',
                             input_ids='R1;R2', method='analysis/growth.md')]
        self.datasets = [dict(id='revenue', path='data/extracted/revenue.csv', stage='extracted', grain='一来源一年营收', coverage='两年', limitations='虚构测试'),
                         dict(id='growth', path='data/curated/growth.csv', stage='curated', grain='两年同比', coverage='两年', limitations='虚构测试')]
        self.save_data()

    def write(self, rel, text):
        p = self.pkg / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')

    def json(self, rel, value):
        self.write(rel, json.dumps(value, ensure_ascii=False, indent=2))

    def csv(self, rel, rows):
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        self.write(rel, out.getvalue())

    def snapshot(self):
        text = '---\n' + '\n'.join(f'{k}: {json.dumps(v, ensure_ascii=False)}' for k, v in self.meta.items()) + '\n---\n\n'
        self.write('raw/sources/M001-input.md', text + '2024 年收入 100 百万元。2025 年收入 125 百万元。')

    def save_data(self):
        self.json('data/datasets.json', self.datasets)
        dictionary = []
        for dataset, rows in zip(self.datasets, [self.extracted, self.curated]):
            self.csv(dataset['path'], rows)
            for field in rows[0]:
                dictionary.append(dict(dataset_id=dataset['id'], field=field, type='string', description='测试字段 '+field,
                                       unit='n/a', missing_rule='空值依公共字段状态规则'))
        self.csv('data/dictionary.csv', dictionary)

    def check(self, **kwargs):
        return checker.Check(self.pkg).run(**kwargs)

    def fails(self, phrase, **kwargs):
        result = self.check(**kwargs)
        self.assertTrue(any(phrase in x for x in result['errors']), result)
        return result

    def review(self):
        self.json('qa/review.json', dict(reviewer='测试夹具，不是实际业务复核', reviewed_digest=checker.review_digest(self.pkg),
                                       checks={k: dict(passed=True, evidence='测试夹具：R1=100，R2=125，G1=(125/100-1)*100=25；报告与原始文本一致') for k in checker.REVIEW_CHECKS}))

    def inventory(self):
        return {p.relative_to(self.pkg).as_posix(): checker.sha256_of(p) for p in self.pkg.rglob('*') if p.is_file()}

    def test_numeric_package_and_seal(self):
        result = self.check()
        self.assertEqual(result['errors'], [], result)
        self.assertEqual(result['stats']['quotes_checked'], 1)
        self.review()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(checker.main([str(self.pkg), '--write-manifest']), 0)
        self.assertEqual(self.check(final=True)['errors'], [])
        self.assertIn('| data_records | 3 |', checker.read(self.pkg/'README.md'))

    def test_qualitative_dataset(self):
        row = dict(record_id='R1', value='支持离线运行', value_type='string', value_origin='reported', status='present',
                   source_id='M001', source_locator='测试文本', original_value='支持离线运行', input_ids='', method='',
                   product='虚构产品', feature='离线')
        self.extracted = [row]
        self.curated = [dict(row, record_id='G1', source_id='', source_locator='', input_ids='R1', method='analysis/growth.md')]
        self.save_data()
        self.assertEqual(self.check()['errors'], [])

    def test_no_data_requires_reason_and_no_empty_tables(self):
        self.config.update(data_status='not_applicable', data_reason='纯文本事实核查无需另建数据集')
        self.json('package.json', self.config)
        self.fails('声明无可用数据却存在数据表')
        for p in (self.pkg/'data').rglob('*'):
            if p.is_file():
                p.unlink()
        report = checker.read(self.pkg/'report.md').replace(' [数据:G1](data/curated/growth.csv)', '')
        self.write('report.md', report)
        self.assertEqual(self.check()['errors'], [])
        self.config['data_reason'] = ''
        self.json('package.json', self.config)
        self.fails('data_reason')

    def test_unparsed_snapshot_is_error_and_counted(self):
        self.write('raw/sources/F001-extra.md', '# 没有元数据')
        r = self.fails('无法解析快照')
        self.assertEqual(r['stats']['snapshot_files'], 2)
        self.assertEqual(r['stats']['snapshots_parsed'], 1)

    def test_yaml_block_list_is_read_without_dropping_metadata(self):
        p = self.pkg/'raw/sources/M001-input.md'
        p.write_text(checker.read(p).replace('original_files: ["raw/files/M001-input.txt"]',
                                           'original_files:\n  - "raw/files/M001-input.txt"'))
        self.assertEqual(self.check()['errors'], [])

    def test_extra_note_formats_and_double_blocks_are_not_silent(self):
        self.write('notes/extra.json', '{"claim": "unparsed"}')
        self.fails('不支持的证据笔记格式')
        p = self.pkg/'notes/M-revenue.md'
        p.write_text(checker.read(p) + '\n- 来源: `M001` · 定位: 第2段\n- 逐字摘录:\n\n  > missing\n')
        self.fails('证据块未解析')

    def test_enum_and_duplicate_source(self):
        self.meta['completeness'] = 'high'
        self.snapshot()
        self.fails('completeness 非法值')
        self.write('raw/sources/M001-duplicate.md', checker.read(self.pkg/'raw/sources/M001-input.md'))
        self.fails('重复来源 ID')

    def test_unparsed_notes_not_silent_pass(self):
        self.write('notes/M-revenue.md', '## Claim 1\n- Source: M001\n- Verbatim: hello\n')
        result = self.fails('检查覆盖为 0')
        self.assertEqual(result['stats']['note_blocks'], 1)

    def test_partial_parse_notes_fails(self):
        self.write('notes/N-other.md', '## 未遵循格式\n只有一个摘要')
        r = self.fails('证据块未解析')
        self.assertEqual(r['stats']['quotes_checked'], 1)
        self.assertEqual(r['stats']['note_blocks'], 2)

    def test_quote_not_in_snapshot(self):
        p = self.pkg/'notes/M-revenue.md'
        p.write_text(checker.read(p).replace('125 百万元', '999 百万元'))
        self.fails('摘录无法按原顺序匹配')

    def test_duplicate_record_and_missing_unit(self):
        self.extracted[1]['record_id'] = 'R1'
        self.extracted[0]['unit'] = ''
        self.save_data()
        self.fails('记录 ID 缺失或重复')
        self.fails('数值记录缺少')

    def test_broken_inputs_and_cycle(self):
        self.curated[0]['input_ids'] = 'missing'
        self.save_data()
        self.fails('输入记录不存在')
        self.curated[0]['input_ids'] = 'G1'
        self.save_data()
        self.fails('存在循环')

    def test_missing_data_not_zero_and_not_input(self):
        self.extracted[0].update(status='missing', value='0', missing_reason='未披露')
        self.save_data()
        self.fails('缺失值须留空')
        self.fails('有值结果依赖缺失输入')

    def test_dictionary_coverage_and_unregistered_csv(self):
        self.write('data/dictionary.csv', 'dataset_id,field,type,description,unit,missing_rule\n')
        self.write('data/curated/orphan.csv', 'value\n3\n')
        self.fails('未登记数据字典')
        self.fails('未登记数据表')

    def test_data_source_and_report_record_link(self):
        self.extracted[0]['source_id'] = 'X999'
        self.save_data()
        self.fails('缺少来源快照')
        self.write('report.md', checker.read(self.pkg/'report.md').replace('数据:G1','数据:unknown'))
        self.fails('报告引用不存在的数据记录')

    def test_unparsed_search_logs_fail(self):
        self.config.update(search_status='performed')
        self.json('package.json', self.config)
        self.write('work/search-logs/M.md', '## 一次检索\nQuery: something')
        self.fails('未识别查询原文')

    def test_search_applicability_matches_actual_queries(self):
        self.write('work/search-logs/M.md', '## 2026-09-27\n- 查询原文: `测试查询`\n')
        self.fails('有实际查询却声明检索不适用')
        self.config['search_status'] = 'performed'
        self.json('package.json', self.config)
        self.assertEqual(self.check()['errors'], [])

    def test_failed_seal_writes_nothing(self):
        before = self.inventory()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(checker.main([str(self.pkg), '--write-manifest']), 1)
        self.assertEqual(before, self.inventory())

    def test_stale_review_and_manifest_extra_file(self):
        self.review()
        self.write('analysis/growth.md', '改过的方法')
        self.fails('人工复核已过期', final=True, sealing=True)
        self.review()
        result = self.check(final=True, sealing=True)
        self.assertEqual(result['errors'], [])
        checker.seal(self.pkg, result)
        self.write('unexpected.txt', '封包后新增')
        self.fails('manifest 未覆盖文件', final=True)

    def test_final_detects_changed_readme(self):
        self.review()
        checker.seal(self.pkg, self.check(final=True, sealing=True))
        self.write('README.md', checker.read(self.pkg/'README.md') + '\n额外修改')
        self.fails('manifest 哈希不一致 README.md', final=True)

    def test_sealed_package_cannot_be_overwritten(self):
        self.review()
        checker.seal(self.pkg, self.check(final=True, sealing=True))
        before = self.inventory()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(checker.main([str(self.pkg), '--write-manifest']), 1)
        self.assertEqual(before, self.inventory())

    def test_path_traversal_and_wrong_source_path(self):
        self.curated[0]['method'] = '../outside.txt'
        self.save_data()
        self.fails('非法包内相对路径')
        self.write('report.md', checker.read(self.pkg/'report.md').replace('(raw/sources/M001-input.md)', '(raw/files/M001-input.txt)'))
        self.fails('路径与来源 ID 不对应')

    def test_legacy_is_read_only_and_cannot_seal(self):
        (self.pkg/'package.json').unlink()
        for name in ('brief.md','plan.md'):
            (self.pkg/'work'/name).rename(self.pkg/name)
        before = self.inventory()
        r = self.check()
        self.assertEqual(r['schema_version'], 1)
        self.assertTrue(any('legacy' in w for w in r['warnings']))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(checker.main([str(self.pkg),'--write-manifest']), 1)
        self.assertEqual(before, self.inventory())

    def test_capture_source_refuses_reused_id_and_roundtrips_quotes(self):
        source = Path(self.tmp.name)/'source.txt'
        source.write_text('original data')
        output = Path(self.tmp.name)/'captured'
        args = [sys.executable, str(SCRIPT_DIR/'capture_source.py'), str(source), '--package',str(output), '--id','U001', '--slug','input', '--title','A "quote", colon: 中文']
        first = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        meta, _ = checker.parse_yaml_header(checker.read(output/'raw/sources/U001-input.md'))
        self.assertEqual(meta['title'], 'A "quote", colon: 中文')
        self.assertEqual(meta['original_files'], ['raw/user-provided/U001-input.txt'])
        before = checker.sha256_of(output/'raw/user-provided/U001-input.txt')
        source.write_text('changed data')
        second = subprocess.run(args, capture_output=True, text=True)
        self.assertNotEqual(second.returncode, 0)
        self.assertIn('id_already_exists', second.stdout)
        self.assertEqual(before, checker.sha256_of(output/'raw/user-provided/U001-input.txt'))


if __name__ == '__main__':
    unittest.main()
