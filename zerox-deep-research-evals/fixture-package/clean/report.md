# 全文检索方案对比（干净样例）

2026-09-26 · 截至 2026-09-26 · 研究包 `clean`

## 执行摘要

**关键结论**

1. SQLite FTS5 提供 BM25 排序。（置信度：高）[1]
2. FTS5 以虚拟表模块形式提供全文检索。（置信度：高）[2]
3. PostgreSQL 的全文检索建立在 tsvector 与 tsquery 之上。（置信度：高）[3]

## 参考来源

- [1] SQLite Project. SQLite FTS5 Documentation. 2026-01-15. https://sqlite.org/fts5.html. 访问 2026-09-26. 来源 ID `M001` 存档 [raw/sources/M001-sqlite-fts5.md](raw/sources/M001-sqlite-fts5.md)
- [2] SQLite Project. SQLite FTS5 Documentation. 2026-01-15. https://sqlite.org/fts5.html. 访问 2026-09-26. 来源 ID `M001` 存档 [raw/sources/M001-sqlite-fts5.md](raw/sources/M001-sqlite-fts5.md)
- [3] PostgreSQL Global Development Group. PostgreSQL 全文检索. 2026-02-20. https://www.postgresql.org/docs/current/textsearch.html. 访问 2026-09-26. 来源 ID `A001` 存档 [raw/sources/A001-pg-fulltext.md](raw/sources/A001-pg-fulltext.md)
