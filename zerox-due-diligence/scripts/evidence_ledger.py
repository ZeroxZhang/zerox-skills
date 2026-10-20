"""按统一契约添加、查询、导出台账并验证引用；更新前保留快照。"""
import argparse

from common import (CONTRACT, cli, emit, fail, load_json, read_project, record, research_errors,
                    save_project, semantic_errors, structural_errors, sync_coverage)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", required=True)
    sub = p.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add", help="添加记录；输入 JSON 为 {表名: [记录]}，支持相互引用的批量记录")
    add.add_argument("--input", required=True)
    add.add_argument("--replace", action="store_true", help="显式按主键更新已有记录，保留更新前快照")
    query = sub.add_parser("query", help="查询一张台账")
    query.add_argument("--table", required=True, choices=list(CONTRACT["tables"]))
    query.add_argument("--field")
    query.add_argument("--value")
    export = sub.add_parser("export", help="导出全部台账与配置为 JSON")
    export.add_argument("--output", required=True)
    sub.add_parser("validate", help="验证结构、语义约束与研报覆盖")
    sub.add_parser("sync-coverage", help="补建必读覆盖项并重算三种最新；不会执行研究或关闭缺口")
    args = p.parse_args()
    cfg, data = read_project(args.project)
    if args.command == "add":
        updates = load_json(args.input)
        if not isinstance(updates, dict) or not updates:
            fail("输入必须为非空表名到记录数组的对象")
        for table, rows in updates.items():
            if table not in CONTRACT["tables"] or not isinstance(rows, list):
                fail(f"未知表或记录不是数组：{table}")
            pk = CONTRACT["tables"][table]["primary_key"]
            seen = set()
            for raw in rows:
                row = record(table, raw)
                if row[pk] in seen:
                    fail(f"同一批次重复主键：{row[pk]}")
                seen.add(row[pk])
                existing = next((i for i, r in enumerate(data[table]) if r[pk] == row[pk]), None)
                if existing is not None:
                    if not args.replace:
                        fail(f"重复主键 {row[pk]}；更新需 --replace")
                    data[table][existing] = row
                else:
                    data[table].append(row)
        errors = structural_errors(data, cfg) + semantic_errors(cfg, data)
        if errors:
            fail("；".join(errors))
        emit({"status": "saved", "backup": str(save_project(args.project, cfg, data)),
              "next": "更新配置后运行 sync-coverage 和 validate"})
    elif args.command == "query":
        if args.field and args.field not in CONTRACT["tables"][args.table]["fields"]:
            fail("未知查询字段")
        rows = data[args.table]
        if args.field:
            rows = [r for r in rows if str(r[args.field]) == args.value]
        emit(rows)
    elif args.command == "export":
        emit({"config": cfg, "tables": data}, args.output)
    elif args.command == "sync-coverage":
        errors = structural_errors(data, cfg) + semantic_errors(cfg, data)
        if errors:
            fail("；".join(errors))
        sync_coverage(cfg, data)
        emit({"status": "saved", "research_gate": cfg["research_gate"],
              "backup": str(save_project(args.project, cfg, data)),
              "note": "开放缺口未自动关闭；人工核对补齐证据后再关闭。"})
    else:
        errors = structural_errors(data, cfg) + semantic_errors(cfg, data) + research_errors(cfg, data)
        emit({"status": "invalid" if errors else "valid_structure", "errors": errors,
              "note": "结构通过不能证明事实真实或研究充分。"})
        return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(cli(main))
