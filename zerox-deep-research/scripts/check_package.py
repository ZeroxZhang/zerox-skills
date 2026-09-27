#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""研究包 v2 检查与封包；旧包只读诊断。只用标准库，不执行包内脚本。"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_META = (
    'id title url final_url author_org published accessed language source_type credibility '
    'conflict_of_interest capture_method completeness original_files sha256 research_line '
    'supersedes archive_url access_note rights_note'
).split()
NULLABLE_META = {'sha256', 'supersedes', 'archive_url'}
ENUMS = {
    'source_type': {'primary', 'secondary', 'tertiary'},
    'credibility': {'A', 'B', 'C', '—', '-'},
    'capture_method': {'script', 'browser', 'fetch-tool', 'snippet', 'metadata-only'},
    'completeness': {'full', 'partial', 'summary', 'snippet-only', 'metadata-only'},
}
CORE_FIELDS = ('record_id value value_type value_origin status source_id source_locator '
               'original_value input_ids method').split()
NUMERIC_FIELDS = 'entity metric unit period geography scope'.split()
REVIEW_CHECKS = ('questions_answered', 'evidence_support', 'data_semantics', 'limitations')
STAT_START, STAT_END = '<!-- package-stats:start -->', '<!-- package-stats:end -->'
ID_RE = re.compile(r'^[A-Z]\d{3}$')
REF_RE = re.compile(r'来源 ID\s*`([A-Z]\d{3})`\s*存档\s*\[[^\]]*\]\(([^)]+)\)')


def read(path):
    return path.read_text(encoding='utf-8-sig')


def sha256_of(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(65536), b''):
            h.update(block)
    return h.hexdigest()


def file_inventory(pkg):
    return sorted(p for p in pkg.rglob('*') if p.is_file())


def review_digest(pkg):
    # README 的机器统计、质检记录与清单在封包时生成；不形成自引用。
    excluded = {'README.md', 'qa/review.json', 'qa/checks.json', 'manifest-sha256.txt'}
    rows = [f'{sha256_of(p)}  {p.relative_to(pkg).as_posix()}'
            for p in file_inventory(pkg) if p.relative_to(pkg).as_posix() not in excluded]
    return hashlib.sha256('\n'.join(rows).encode()).hexdigest()


def normalize(s):
    s = re.sub(r'^\s{0,3}[#>]+\s*', '', s, flags=re.M)
    s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)
    s = re.sub(r'[`*_~]', '', s)
    for a, b in [('“', '"'), ('”', '"'), ('‘', "'"), ('’', "'"), ('，', ','), ('。', '.'), ('：', ':'), ('（', '('), ('）', ')')]:
        s = s.replace(a, b)
    return re.sub(r'\s+', ' ', s).strip().casefold()


def scalar(raw):
    raw = raw.strip()
    if raw == 'null':
        return None
    if raw.startswith('"') or raw.startswith('['):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            if raw.startswith('[') and raw.endswith(']'):
                return [scalar(x) for x in next(csv.reader([raw[1:-1]], skipinitialspace=True))] if raw[1:-1].strip() else []
            raise ValueError('双引号字段须为 JSON 兼容字符串')
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1].replace("''", "'")
    return raw


def parse_yaml_header(text):
    # 明确支持采集器输出的扁平 YAML；不静默吞掉不支持的格式。
    m = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
    if not m:
        raise ValueError('缺少有效 YAML 元数据头')
    meta = {}
    list_key = None
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        item = re.match(r'^\s+-\s+(.+)$', line)
        if item and list_key:
            meta[list_key].append(scalar(item[1]))
            continue
        match = re.match(r'^([a-z_][a-z_0-9]*):\s*(.*)$', line)
        if not match or match[1] in meta:
            raise ValueError('不支持或重复的元数据字段: ' + line[:80])
        list_key = match[1] if not match[2] and match[1] in {'original_files', 'subquestions'} else None
        meta[match[1]] = [] if list_key else scalar(match[2])
    return meta, text[m.end():]


class Check:
    def __init__(self, pkg):
        self.pkg = Path(pkg).expanduser().resolve()
        self.errors, self.warnings = [], []
        self.stats = {}
        self.snapshots, self.records = {}, {}
        self.version = 1
        self.config = {}

    def error(self, message):
        self.errors.append(message)

    def path(self, rel, context, must_exist=True):
        if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or '..' in Path(rel).parts or '\\' in rel:
            self.error(f'{context}: 非法包内相对路径 {rel!r}')
            return None
        p = self.pkg / rel
        if not p.resolve().is_relative_to(self.pkg):
            self.error(f'{context}: 路径越出研究包 {rel}')
            return None
        if must_exist and not p.is_file():
            self.error(f'{context}: 文件不存在 {rel}')
            return None
        return p

    def json_file(self, rel):
        p = self.path(rel, rel)
        if not p:
            return None
        try:
            return json.loads(read(p))
        except (ValueError, UnicodeError) as e:
            self.error(f'{rel}: JSON 无法解析: {e}')
            return None

    def csv_file(self, rel):
        p = self.path(rel, rel)
        if not p:
            return [], []
        try:
            reader = csv.DictReader(io.StringIO(read(p)), strict=True)
            fields = reader.fieldnames or []
            if not fields or len(fields) != len(set(fields)) or any(not f for f in fields):
                self.error(f'{rel}: 缺少表头或字段重复')
            rows = list(reader)
            if any(None in r or any(v is None for v in r.values()) for r in rows):
                self.error(f'{rel}: 数据行与表头列数不一致')
                return fields, []
            return fields, rows
        except (ValueError, csv.Error, UnicodeError) as e:
            self.error(f'{rel}: CSV 无法解析: {e}')
            return [], []

    def package(self):
        for p in self.pkg.rglob('*'):
            if p.is_symlink():
                self.error(f'不接受符号链接: {p.relative_to(self.pkg)}')
        if (self.pkg / 'package.json').exists():
            self.config = self.json_file('package.json')
            if not isinstance(self.config, dict):
                self.error('package.json 须为对象')
                self.config = {}
            self.version = self.config.get('schema_version')
            if type(self.version) is not int or self.version != 2:
                self.error('不支持的 schema_version；当前只支持 2，缺少标记按 legacy v1 诊断')
        else:
            self.warnings.append('legacy v1：只读诊断；不迁移、不封包，不宣称符合 v2')
        required = ['report.md', 'sources.md', 'README.md']
        required += ['work/brief.md', 'work/plan.md'] if self.version == 2 else ['brief.md', 'plan.md']
        for rel in required:
            p = self.path(rel, '研究包')
            if p and not read(p).strip():
                self.error(f'{rel}: 空文件')
        if self.version == 2:
            for key in ('package_id', 'topic', 'information_cutoff', 'data_status', 'data_reason', 'search_status', 'search_reason'):
                if not isinstance(self.config.get(key), str) or not self.config[key].strip():
                    self.error(f'package.json 缺少非空字符串 {key}')
            if self.config.get('data_status') not in {'available', 'unavailable', 'not_applicable'}:
                self.error('data_status 须为 available / unavailable / not_applicable')
            if self.config.get('search_status') not in {'performed', 'not_applicable'}:
                self.error('search_status 须为 performed / not_applicable')
            for old in ('brief.md', 'plan.md', 'tasks', 'raw/search-logs'):
                if (self.pkg / old).exists():
                    self.error(f'v2 混入旧布局 {old}；使用 work/，不要保留两份真源')

    def sources(self):
        for p in (self.pkg / 'raw/sources').rglob('*'):
            if p.is_file() and (p.suffix != '.md' or p.parent != self.pkg / 'raw/sources'):
                self.error(f'快照文件未遵循一级 Markdown 布局: {p.relative_to(self.pkg)}')
        files = sorted((self.pkg / 'raw/sources').glob('*.md'))
        self.stats['snapshot_files'] = len(files)
        originals = set()
        for p in files:
            try:
                meta, body = parse_yaml_header(read(p))
            except (ValueError, UnicodeError) as e:
                self.error(f'{p.name}: 无法解析快照: {e}')
                continue
            sid = meta.get('id')
            if not isinstance(sid, str) or not ID_RE.fullmatch(sid):
                self.error(f'{p.name}: 无效来源 ID {sid!r}')
                continue
            if sid in self.snapshots:
                self.error(f'{p.name}: 重复来源 ID {sid}')
                continue
            self.snapshots[sid] = (p, meta, body)
            if p.name.split('-')[0] != sid:
                self.error(f'{p.name}: 文件名与来源 ID {sid} 不一致')
            for key in REQUIRED_META:
                if key not in meta or (meta[key] in (None, '') and not (key in NULLABLE_META and meta[key] is None)):
                    self.error(f'{p.name}: 缺少元数据字段 {key}')
            for key, allowed in ENUMS.items():
                if not isinstance(meta.get(key), str) or meta[key] not in allowed:
                    self.error(f'{p.name}: {key} 非法值 {meta.get(key)!r}')
            raw = meta.get('original_files')
            if not isinstance(raw, list) or any(not isinstance(x, str) for x in raw):
                self.error(f'{p.name}: original_files 须为路径列表')
                raw = []
            for rel in raw:
                self.path(rel, sid)
                originals.add(rel)
            digest = meta.get('sha256')
            if raw:
                if not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{64}', digest):
                    self.error(f'{sid}: 有原始文件但缺少有效 sha256（对应第一个原始文件）')
                else:
                    original = self.path(raw[0], sid)
                    if original and sha256_of(original) != digest:
                        self.error(f'{sid}: 原始文件哈希不一致')
            elif digest is not None:
                self.error(f'{sid}: 无原始文件时 sha256 须为 null')
            if meta.get('completeness') in {'full', 'partial'} and not body.strip():
                self.error(f'{sid}: 声称有正文但快照为空')
        self.stats['snapshots_parsed'] = len(self.snapshots)
        self.stats['completeness'] = dict(Counter(str(m.get('completeness')) for _, m, _ in self.snapshots.values()))
        index = {}
        p = self.pkg / 'sources.md'
        if p.exists():
            for line in read(p).splitlines():
                cells = [c.strip() for c in line.strip().strip('|').split('|')]
                if not line.startswith('|') or not cells or not ID_RE.fullmatch(cells[0]):
                    continue
                if cells[0] in index:
                    self.error('sources.md 重复来源 ID ' + cells[0])
                index[cells[0]] = cells
        for sid in self.snapshots.keys() - index.keys():
            self.error(f'{sid}: 快照未登记 sources.md')
        for sid in index.keys() - self.snapshots.keys():
            self.error(f'{sid}: 索引没有可解析快照')
        for sid in index.keys() & self.snapshots.keys():
            cells, (p, meta, _) = index[sid], self.snapshots[sid]
            if len(cells) < 13:
                self.error(f'{sid}: 来源索引不足 13 列')
                continue
            if cells[7] != meta.get('completeness') or cells[8] != meta.get('capture_method'):
                self.error(f'{sid}: 来源索引与快照完整度或采集方式不一致')
            if p.relative_to(self.pkg).as_posix() not in cells[9]:
                self.error(f'{sid}: 来源索引缺少快照路径')
        for folder in ('raw/files', 'raw/user-provided'):
            for p in (self.pkg / folder).rglob('*'):
                if p.is_file() and p.relative_to(self.pkg).as_posix() not in originals:
                    self.error(f'未登记原始附件: {p.relative_to(self.pkg)}')
        if not files:
            self.error('没有来源快照；不能完成证据核验')

    def notes(self):
        for p in (self.pkg / 'notes').rglob('*'):
            if p.is_file() and p.suffix != '.md':
                self.error(f'不支持的证据笔记格式: {p.relative_to(self.pkg)}')
        files = sorted((self.pkg / 'notes').rglob('*.md'))
        counts = {'notes_files': len(files), 'note_blocks': 0, 'quotes_checked': 0}
        for p in files:
            body = read(p)
            blocks = re.split(r'^##\s+', body, flags=re.M)[1:]
            if not blocks:
                self.error(f'{p.name}: 未识别证据块；须使用 notes 模板的二级标题')
            for block in blocks:
                counts['note_blocks'] += 1
                src = re.search(r'^- 来源:\s*`([A-Z]\d{3})`\s*·\s*定位:\s*(\S.*)$', block, re.M)
                quoted = re.search(r'^- 逐字摘录:\s*\n((?:\s*\n|[ \t]*>[^\n]*(?:\n|$))+)', block, re.M)
                if not src or not quoted or len(re.findall(r'^- 来源:', block, re.M)) != 1 or len(re.findall(r'^- 逐字摘录:', block, re.M)) != 1:
                    self.error(f'{p.name}: 证据块未解析，来源/定位/逐字摘录格式不完整: {block.splitlines()[0]}')
                    continue
                sid = src[1]
                if sid not in self.snapshots:
                    self.error(f'{p.name}: 摘录来源不存在 {sid}')
                    continue
                quote = '\n'.join(re.sub(r'^\s*>\s?', '', line) for line in quoted[1].splitlines() if line.lstrip().startswith('>'))
                fragments = [normalize(x) for x in re.split(r'\[\.\.\.\]', quote) if normalize(x)]
                counts['quotes_checked'] += 1
                snapshot = normalize(self.snapshots[sid][2])
                position = 0
                if not fragments:
                    self.error(f'{p.name}: 摘录为空 {sid}')
                for fragment in fragments:
                    match = snapshot.find(fragment, position)
                    if match < 0:
                        self.error(f'{p.name}: 摘录无法按原顺序匹配 {sid}')
                        break
                    position = match + len(fragment)
        if not files or not counts['quotes_checked']:
            self.error('摘录检查覆盖为 0，不能声称已核验')
        self.stats.update(counts)

    def logs(self):
        folder = 'work/search-logs' if self.version == 2 else 'raw/search-logs'
        for p in (self.pkg / folder).rglob('*'):
            if p.is_file() and p.suffix != '.md':
                self.error(f'不支持的检索日志格式: {p.relative_to(self.pkg)}')
        files = sorted((self.pkg / folder).rglob('*.md'))
        blocks = queries = 0
        for p in files:
            parts = re.split(r'^##\s+', read(p), flags=re.M)[1:]
            if not parts:
                self.error(f'{p.name}: 检索日志无法解析')
            for part in parts:
                blocks += 1
                n = len(re.findall(r'^- 查询原文:\s*\S', part, re.M))
                queries += n
                if not n:
                    self.error(f'{p.name}: 检索日志块未识别查询原文')
        self.stats.update(search_files=len(files), search_blocks=blocks, search_queries=queries)
        if queries and self.version == 2 and self.config.get('search_status') == 'not_applicable':
            self.error('有实际查询却声明检索不适用；search_status 应为 performed')
        if not queries and not (self.version == 2 and self.config.get('search_status') == 'not_applicable'):
            self.error('检索查询覆盖为 0；无联网或仅用户材料须显式说明不适用')

    def data(self):
        self.stats.update(datasets=0, data_records=0, derived_records=0)
        if self.version != 2:
            self.warnings.append('legacy v1 未定义数据契约；未执行数据集验收')
            return
        if self.config.get('data_status') != 'available':
            if any((self.pkg / 'data').rglob('*.csv')) or (self.pkg / 'data/datasets.json').exists():
                self.error('声明无可用数据却存在数据表或目录；须如实设置 data_status')
            return
        self.path('data/README.md', '数据包')
        datasets = self.json_file('data/datasets.json')
        if not isinstance(datasets, list) or not datasets:
            self.error('data/datasets.json 须为非空数据集列表')
            return
        dict_fields, dictionary = self.csv_file('data/dictionary.csv')
        if not {'dataset_id', 'field', 'type', 'description', 'unit', 'missing_rule'} <= set(dict_fields):
            self.error('数据字典缺少必填列')
        definitions = {}
        for row in dictionary:
            key = (row.get('dataset_id'), row.get('field'))
            if key in definitions:
                self.error(f'数据字典重复字段 {key}')
            if not all(row.get(x, '').strip() for x in ('dataset_id', 'field', 'type', 'description', 'unit', 'missing_rule')):
                self.error(f'数据字典字段说明不完整 {key}')
            if row.get('type') not in {'string', 'number', 'boolean'}:
                self.error(f'数据字典字段类型无效 {key}')
            definitions[key] = row
        ids, paths, used_definitions = set(), set(), set()
        for dataset in datasets:
            if not isinstance(dataset, dict) or not all(isinstance(dataset.get(k), str) and dataset[k].strip() for k in ('id', 'path', 'stage', 'grain', 'coverage', 'limitations')):
                self.error('数据集登记缺少 id/path/stage/grain/coverage/limitations')
                continue
            did, rel, stage = dataset['id'], dataset['path'], dataset['stage']
            if did in ids or rel in paths:
                self.error(f'数据集 ID 或路径重复: {did} {rel}')
            ids.add(did)
            paths.add(rel)
            if stage not in {'extracted', 'curated'} or not rel.startswith(f'data/{stage}/') or not rel.endswith('.csv'):
                self.error(f'{did}: stage 与 CSV 路径不一致')
            fields, rows = self.csv_file(rel)
            if not set(CORE_FIELDS) <= set(fields):
                self.error(f'{did}: 缺少公共字段 {sorted(set(CORE_FIELDS) - set(fields))}')
            if not rows:
                self.error(f'{did}: 空数据集，不能用空壳交付')
            for field in fields:
                used_definitions.add((did, field))
                if (did, field) not in definitions:
                    self.error(f'{did}: 字段 {field} 未登记数据字典')
            for row in rows:
                rid = row.get('record_id', '')
                if not rid or rid in self.records:
                    self.error(f'{did}: 记录 ID 缺失或重复 {rid!r}')
                    continue
                self.records[rid] = (row, rel, stage)
                for field, value in row.items():
                    kind = definitions.get((did, field), {}).get('type')
                    if value and kind == 'number' and not finite_number(value):
                        self.error(f'{rid}: {field} 不是有限数值')
                    if value and kind == 'boolean' and value not in {'true', 'false'}:
                        self.error(f'{rid}: {field} 不是 true/false')
                status = row.get('status')
                if status not in {'present', 'missing', 'unavailable', 'not_applicable'}:
                    self.error(f'{rid}: 无效数据状态')
                if status == 'present':
                    if not row.get('value', '').strip():
                        self.error(f'{rid}: present 记录缺少值')
                elif row.get('value') or not row.get('missing_reason', '').strip():
                    self.error(f'{rid}: 缺失值须留空并记录 missing_reason，不能填 0')
                if row.get('value_type') not in {'number', 'string', 'boolean'}:
                    self.error(f'{rid}: 无效 value_type')
                if row.get('value_type') == 'number':
                    if status == 'present' and not finite_number(row.get('value', '')):
                        self.error(f'{rid}: 数值无效，不接受单位混写、NaN 或 Infinity')
                    if not all(row.get(x, '').strip() for x in NUMERIC_FIELDS):
                        self.error(f'{rid}: 数值记录缺少对象/指标/单位/期间/地域/口径')
                if row.get('value_type') == 'boolean' and status == 'present' and row.get('value') not in {'true', 'false'}:
                    self.error(f'{rid}: 布尔值须为 true/false')
                origin = row.get('value_origin')
                if origin not in {'reported', 'estimate', 'derived'}:
                    self.error(f'{rid}: 无效 value_origin')
                if stage == 'extracted':
                    if origin == 'derived' or row.get('input_ids') or row.get('method'):
                        self.error(f'{rid}: 提取层不得放本次派生计算')
                    if status == 'present':
                        sid = row.get('source_id')
                        if sid not in self.snapshots or not row.get('source_locator', '').strip() or not row.get('original_value', '').strip():
                            self.error(f'{rid}: 缺少来源快照、定位或原始表述')
                        elif self.snapshots[sid][1].get('completeness') not in {'full', 'partial'}:
                            # 二进制原始数据可作为证据，须人工核对表/单元格，不把 metadata-only 当逐字正文。
                            meta = self.snapshots[sid][1]
                            if not meta.get('original_files'):
                                self.error(f'{rid}: 来源既无可核对正文，也无原始数据文件')
                else:
                    if not row.get('input_ids', '').strip() or not row.get('method', '').strip():
                        self.error(f'{rid}: 整理层须有输入记录和方法路径（原样选用也要说明）')
                    if row.get('source_id') or row.get('source_locator'):
                        self.error(f'{rid}: 整理层通过 input_ids 追溯，不手写第二份来源映射')
                    method = row.get('method', '')
                    if not method.startswith('analysis/'):
                        self.error(f'{rid}: method 须指向 analysis/ 下的脚本或算式说明')
                    self.path(method, rid)
        for key in definitions.keys() - used_definitions:
            self.error(f'数据字典存在无对应数据列的条目 {key}')
        for p in (self.pkg / 'data').rglob('*.csv'):
            rel = p.relative_to(self.pkg).as_posix()
            if rel != 'data/dictionary.csv' and rel not in paths:
                self.error('未登记数据表: ' + rel)
        graph = {}
        for rid, (row, _, stage) in self.records.items():
            inputs = [x.strip() for x in row.get('input_ids', '').split(';') if x.strip()]
            graph[rid] = inputs
            for value in inputs:
                if value not in self.records:
                    self.error(f'{rid}: 输入记录不存在 {value}')
                elif row.get('status') == 'present' and self.records[value][0].get('status') != 'present':
                    self.error(f'{rid}: 有值结果依赖缺失输入 {value}')
        # 拓扑消去，避免递归深度随记录数增长。
        remaining = {k: set(v) & self.records.keys() for k, v in graph.items()}
        while remaining:
            ready = {k for k, v in remaining.items() if not v}
            if not ready:
                self.error('数据派生关系存在循环: ' + ', '.join(sorted(remaining)[:10]))
                break
            remaining = {k: v - ready for k, v in remaining.items() if k not in ready}
        self.stats.update(datasets=len(ids), data_records=len(self.records),
                          derived_records=sum(r.get('value_origin') == 'derived' for r, _, _ in self.records.values()))

    def report(self):
        p = self.pkg / 'report.md'
        if not p.exists():
            return
        text = read(p)
        parts = re.split(r'^##\s*参考来源\s*$', text, maxsplit=1, flags=re.M)
        if len(parts) != 2:
            self.error('report.md 缺少「## 参考来源」')
            return
        body, section = parts
        refs = {}
        for line in section.splitlines():
            head = re.match(r'^- \[(\d+)\]', line)
            if not head:
                continue
            n = head[1]
            tail = REF_RE.search(line)
            if n in refs:
                self.error(f'重复参考编号 [{n}]')
            refs[n] = tail
            if not tail:
                self.error(f'[{n}]: 参考条目格式无法解析')
                continue
            sid, rel = tail.groups()
            target = self.path(rel, f'参考 [{n}]')
            if sid not in self.snapshots:
                self.error(f'[{n}]: 来源无可解析快照 {sid}')
            elif target and target != self.snapshots[sid][0]:
                self.error(f'[{n}]: 路径与来源 ID 不对应')
            elif self.snapshots[sid][1].get('completeness') not in {'full', 'partial'}:
                self.warnings.append(f'[{n}]: 正文完整度不足，须人工检查原始文件或其他支撑来源')
        cites = set(re.findall(r'\[(\d+)(?:,\s*[^\]]*)?\](?!\()', re.sub(r'```.*?```', '', body, flags=re.S)))
        for n in cites - refs.keys():
            self.error(f'正文引用 [{n}] 无参考条目')
        for n in refs.keys() - cites:
            self.warnings.append(f'参考 [{n}] 未被正文引用')
        if not cites or not refs:
            self.error('报告引用检查覆盖为 0')
        self.stats.update(reference_entries=len(refs), cited_sources=len({refs[n][1] for n in cites & refs.keys() if refs[n]}))
        data_refs = re.findall(r'\[数据:([^\]]+)\]\(([^)]+)\)', body)
        for rid, rel in data_refs:
            target = self.path(rel, f'报告数据 {rid}')
            if rid not in self.records:
                self.error(f'报告引用不存在的数据记录 {rid}')
            elif target and rel != self.records[rid][1]:
                self.error(f'报告数据 {rid} 的文件路径不匹配')
        self.stats['report_data_links'] = len(data_refs)
        if self.version == 2 and self.config.get('data_status') == 'available' and not data_refs:
            self.error('数据可用但报告没有记录级数据引用；关键数据必须关联，全面性仍须人工核验')

    def manual(self):
        review = self.json_file('qa/review.json')
        if not isinstance(review, dict):
            self.error('缺少有效人工复核记录')
            return
        if not isinstance(review.get('reviewer'), str) or not review['reviewer'].strip():
            self.error('人工复核须记录实际执行者')
        if review.get('reviewed_digest') != review_digest(self.pkg):
            self.error('人工复核已过期或未绑定当前内容；重新核验后更新 reviewed_digest')
        checks = review.get('checks')
        if not isinstance(checks, dict):
            checks = {}
        for key in REVIEW_CHECKS:
            item = checks.get(key)
            if not isinstance(item, dict) or item.get('passed') is not True or not isinstance(item.get('evidence'), str) or not item['evidence'].strip():
                self.error(f'人工复核未完成 {key}：须有 passed=true 和核验位置/理由')

    def manifest(self):
        p = self.path('manifest-sha256.txt', '封包清单')
        if not p:
            return
        listed = set()
        for line in read(p).splitlines():
            m = re.fullmatch(r'([a-f0-9]{64})  (.+)', line)
            if not m:
                self.error('manifest 存在无法解析的行')
                continue
            digest, rel = m.groups()
            if rel in listed or rel == 'manifest-sha256.txt':
                self.error(f'manifest 重复或自引用 {rel}')
            listed.add(rel)
            target = self.path(rel, 'manifest')
            if target and sha256_of(target) != digest:
                self.error(f'manifest 哈希不一致 {rel}')
        actual = {x.relative_to(self.pkg).as_posix() for x in file_inventory(self.pkg)} - {'manifest-sha256.txt'}
        for rel in actual - listed:
            self.error('manifest 未覆盖文件 ' + rel)
        if not listed:
            self.error('manifest 为空')

    def run(self, final=False, sealing=False):
        self.package()
        # 符号链接不参与后续读取或散列。
        if any('符号链接' in e for e in self.errors):
            return self.result(final)
        self.sources()
        self.notes()
        self.logs()
        self.data()
        self.report()
        if final:
            if self.version != 2:
                self.error('只有 v2 包可以通过最终验收或封包')
            else:
                self.manual()
                p = self.pkg / 'README.md'
                if p.exists() and (read(p).count(STAT_START) != 1 or read(p).count(STAT_END) != 1 or read(p).find(STAT_START) > read(p).find(STAT_END)):
                    self.error('README 缺少唯一且有序的机器统计标记')
                if not sealing:
                    self.manifest()
                    saved = self.json_file('qa/checks.json')
                    if not isinstance(saved, dict) or saved.get('status') != 'FINALIZED' or saved.get('reviewed_digest') != review_digest(self.pkg):
                        self.error('封包检查记录缺失或已过期')
        return self.result(final)

    def result(self, final):
        return dict(schema_version=self.version, status='FAIL' if self.errors else ('PASS_FINAL' if final else 'PASS_AUTOMATED'),
                    errors=self.errors, warnings=self.warnings, stats=self.stats,
                    manual_review='required' if not final else ('blocked' if self.errors else 'recorded'),
                    checked_at=datetime.now(timezone.utc).isoformat(timespec='seconds'))


def finite_number(value):
    from decimal import Decimal, InvalidOperation
    try:
        return Decimal(value).is_finite()
    except (InvalidOperation, ValueError, TypeError):
        return False


def seal(pkg, result):
    # 仅在自动检查和绑定当前内容的人工复核均通过后写入。
    result = dict(result, status='FINALIZED', reviewed_digest=review_digest(pkg))
    stats = result['stats']
    block = '\n\n自动检查与人工复核记录已通过；最终状态以重新运行 `check_package.py --final` 为准。\n\n'
    block += '| 检查项 | 数量 |\n|---|---:|\n'
    block += '\n'.join(f'| {key} | {stats.get(key, 0)} |' for key in
                       ('snapshot_files', 'snapshots_parsed', 'notes_files', 'note_blocks', 'quotes_checked', 'search_queries', 'datasets', 'data_records', 'derived_records', 'report_data_links'))
    block += '\n\n'
    p = pkg / 'README.md'
    text = read(p)
    before, rest = text.split(STAT_START)
    _, after = rest.split(STAT_END)
    p.write_text(before + STAT_START + block + STAT_END + after, encoding='utf-8')
    (pkg / 'qa').mkdir(exist_ok=True)
    (pkg / 'qa/checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    rows = [f'{sha256_of(p)}  {p.relative_to(pkg).as_posix()}' for p in file_inventory(pkg) if p != pkg / 'manifest-sha256.txt']
    (pkg / 'manifest-sha256.txt').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package')
    parser.add_argument('--json', action='store_true')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--final', action='store_true', help='只读核验封包、人工复核绑定与完整性清单')
    mode.add_argument('--write-manifest', action='store_true', help='v2 最终验收通过后生成统计、检查记录与清单；失败不写文件')
    mode.add_argument('--review-digest', action='store_true', help='输出人工复核应绑定的内容指纹；不代表复核通过')
    args = parser.parse_args(argv)
    pkg = Path(args.package).expanduser().resolve()
    if not pkg.is_dir():
        parser.error('研究包目录不存在')
    if args.review_digest:
        if any(p.is_symlink() for p in pkg.rglob('*')):
            parser.error('研究包不能包含符号链接')
        print(review_digest(pkg))
        return 0
    try:
        result = Check(pkg).run(final=args.final or args.write_manifest, sealing=args.write_manifest)
        if args.write_manifest:
            if (pkg / 'manifest-sha256.txt').exists():
                result['errors'].append('已有封包清单；请用 --final 验证，修订须创建新版本目录')
                result['status'] = 'FAIL'
            elif not result['errors']:
                result = seal(pkg, result)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as e:
        result = dict(status='FAIL', errors=[f'文件或格式错误: {type(e).__name__}: {e}'], warnings=[], stats={})
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result['status'])
        for key in ('errors', 'warnings'):
            print(f'{key}: {len(result[key])}')
            for message in result[key]:
                print('  ' + message)
        print(json.dumps(result['stats'], ensure_ascii=False, indent=2))
        if result['status'] == 'PASS_AUTOMATED':
            print('仅自动检查通过；证据含义、关键数字覆盖、计算正确性仍须人工核验。')
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    sys.exit(main())
