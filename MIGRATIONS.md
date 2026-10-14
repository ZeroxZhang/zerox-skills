# Skill migrations / 技能迁移记录

[中文](#中文) | [English](#english)

<a id="中文"></a>

## 中文

2026-10-14，将下列 7 个技能从各自仓库复制到本仓库，统一为 `zerox-*` 名称。新目录是后续维护入口，迁入成员保留原有业务流程，不自动纳入原报告套件的编排。

表中的提交是迁移前记录的源仓库 HEAD，链接到完整提交 SHA，用于说明复制基准。

| 来源仓库 / Source repository | 新名称与路径 / New name and path | 源 HEAD / Source HEAD |
|---|---|---|
| [onepager](https://github.com/ZeroxZhang/onepager) | [zerox-onepager](zerox-onepager/) | [`de755abaea53`](https://github.com/ZeroxZhang/onepager/commit/de755abaea53eba3e95327cbc4082069fa2108c0) |
| [paper-to-course](https://github.com/ZeroxZhang/paper-to-course) | [zerox-paper-to-course](zerox-paper-to-course/) | [`e639abbbded8`](https://github.com/ZeroxZhang/paper-to-course/commit/e639abbbded8bcee5053d5dd93474bd5e3080deb) |
| [really](https://github.com/ZeroxZhang/really) | [zerox-really](zerox-really/) | [`aaf2ca58309f`](https://github.com/ZeroxZhang/really/commit/aaf2ca58309f7794359b6397478891fb78ead86a) |
| [ins-photo-downloader](https://github.com/ZeroxZhang/ins-photo-downloader) | [zerox-ins-photo-downloader](zerox-ins-photo-downloader/) | [`2649877d0efc`](https://github.com/ZeroxZhang/ins-photo-downloader/commit/2649877d0efc1871c18a9139cb31c48920f17365) |
| [arch_diagram](https://github.com/ZeroxZhang/arch_diagram) | [zerox-architecture-diagram](zerox-architecture-diagram/) | [`7e50533fc1c2`](https://github.com/ZeroxZhang/arch_diagram/commit/7e50533fc1c2f409ba3fd471846889ebe3b212c3) |
| [consultancy_charts_concise](https://github.com/ZeroxZhang/consultancy_charts_concise) | [zerox-consulting-deck-skill-concise](zerox-consulting-deck-skill-concise/) | [`3312ddd7bbf5`](https://github.com/ZeroxZhang/consultancy_charts_concise/commit/3312ddd7bbf5069ee30774f5ce4d4b0004d85592) |
| [consulting-report-forge](https://github.com/ZeroxZhang/consulting-report-forge) | [zerox-consulting-report-forge](zerox-consulting-report-forge/) | [`d8bd50ac6506`](https://github.com/ZeroxZhang/consulting-report-forge/commit/d8bd50ac6506b5e1d4175195b7aaaad8bd16281a) |

迁移以源仓库的 Git 跟踪文件为基准，保留正式示例、字体、开发文档、测试与许可证。排除 `.git`、`.DS_Store`、`.claude/` 本机工具配置、缓存、依赖环境、私有资料与会话记录；不将这些文件作为技能内容发布。

`really/really/` 与 `consultancy_charts_concise/consulting_deck_skill_concise/` 中的技能入口已展平到对应新成员的一级目录，原仓库的配套文件一并保留。迁移修正技能名称、调用方式、安装与维护地址，以及必要的相对引用；不重写技能业务流程。

历史截图、样张与开发记录可能保留旧名称或旧地址，它们仍是历史资料。已有产物格式名按兼容需要保留，例如 `.onepager/`、`onepager.ir.json`；新构建使用 `zerox-onepager` 标识，同时接受历史 `onepager` 构建记录。

原仓库的 workflow 文件保留在各成员的 `.github/` 下作为来源记录；本次未建立仓库根 CI，这些文件不会自动成为本仓库的 GitHub Actions 工作流。

旧仓库不删除、不归档，原技能代码保留；迁移对旧仓库的变更仅限 README 中的新地址与停更说明。后续维护在本仓库进行，运行依赖和验证方法见各成员文档。

---

<a id="english"></a>

## English

On 2026-10-14, the seven skills listed above were copied from their individual repositories into this repository and renamed to `zerox-*`. Their new directories are the maintenance entry points. Migrated members retain their original workflows and do not automatically join the original reporting suite's orchestration.

The shared table records each source repository's HEAD captured before migration and links to its full commit SHA. These revisions identify the copy baseline.

The migration uses Git-tracked source files as its baseline, preserving curated examples, fonts, development documents, tests and licenses. It excludes `.git`, `.DS_Store`, local `.claude/` configuration, caches, dependency environments, private materials and session records; those files are not published as skill content.

The skill entries under `really/really/` and `consultancy_charts_concise/consulting_deck_skill_concise/` were flattened into their respective direct child directories, while retaining accompanying repository files. Migration adaptations update skill names, invocation, installation and maintenance addresses, and necessary relative references without rewriting business workflows.

Historical screenshots, samples and development records may retain former names or addresses. Existing artifact formats are preserved where compatibility requires them, including `.onepager/` and `onepager.ir.json`. New builds identify themselves as `zerox-onepager`, while historical `onepager` build records remain accepted.

Source workflow files are retained under the members' `.github/` directories as provenance. No repository-root CI was established in this migration, so these files do not automatically run as this repository's GitHub Actions workflows.

The original repositories are retained without deletion or archival, and their skill code remains in place. Migration changes in those repositories are limited to README notices giving the new address and stating that maintenance has moved. Future maintenance takes place here; consult each member's documentation for runtime dependencies and validation methods.
