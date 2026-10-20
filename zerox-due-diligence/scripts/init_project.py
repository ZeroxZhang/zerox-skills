"""初始化独立工作区，不覆盖已有路径。"""
import argparse
import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from common import CONTRACT, ROOT, cli, csv_text, dumps, fail, iso_date, load_json, record, safe_write, sync_coverage


def initialize(output, target, purpose=None, depth="Standard", as_of=None, timezone="Asia/Shanghai",
               registration_id="", geography="", listing_status="unknown", exchange="", security_code="",
               enable_scoring=False):
    output = Path(output)
    if output.exists():
        fail(f"输出路径已存在，请选择新目录：{output}")
    if not target.strip():
        fail("目标名称不能为空")
    if purpose is not None and purpose not in CONTRACT["enums"]["purpose"]:
        fail("未知目的")
    if enable_scoring and purpose not in CONTRACT["scoring"]["purposes"]:
        fail("只有已明确的决策目的可启用评分；公司研究不评分")
    if depth not in CONTRACT["enums"]["depth"]:
        fail("未知深度")
    try:
        today = datetime.now(ZoneInfo(timezone)).date().isoformat()
    except ZoneInfoNotFoundError as exc:
        fail(f"无可用时区数据：{timezone}；可传 --timezone UTC")
    as_of = as_of or today
    iso_date(as_of)
    cfg = load_json(ROOT / "templates/project-config.json")
    cfg.update(target=target, purpose=purpose, purpose_status="confirmed" if purpose else "pending",
               depth=depth, as_of_date=as_of, timezone=timezone, historical=as_of < today,
               geography=geography, scoring_enabled=enable_scoring)
    data = {name: [] for name in CONTRACT["tables"]}
    data["entity-map"] = [record("entity-map", {
        "entity_id": cfg["target_id"], "legal_name": target, "registration_id": registration_id,
        "geography": geography, "entity_type": "legal_entity", "identity_status": "pending",
        "listing_status": listing_status, "exchange": exchange, "security_code": security_code,
        "identity_notes": "用户输入，仅为待核实身份；需补登记证据和控制链核查。"})]
    if enable_scoring:
        for n, (dimension, weight) in enumerate(CONTRACT["scoring"]["purposes"][purpose]["weights"].items(), 1):
            data["scorecard"].append(record("scorecard", {
                "score_id": f"SC-{n:04}", "purpose": purpose, "dimension": dimension, "weight": weight,
                "applicability": "applicable", "confidence": "unknown", "coverage_status": "missing",
                "reason": "尚未取得足够评分证据"}))
    sync_coverage(cfg, data)
    output.mkdir(parents=False, exist_ok=False)
    for name, rows in data.items():
        safe_write(output / f"{name}.csv", csv_text(name, rows))
    safe_write(output / "project-config.json", dumps(cfg))
    for name in ("financial-input.json", "report-content.json", "request-list.md", "interview-outline.md"):
        shutil.copyfile(ROOT / "templates" / name, output / name)
    for folder in ("materials", "modules", "reports"):
        (output / folder).mkdir()
    return {"status": "created", "path": str(output.resolve()), "research_gate": cfg["research_gate"],
            "note": "仅初始化工作区；未执行检索、身份核验或研报阅读。"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="不存在的新目录；父目录须存在")
    parser.add_argument("--target", required=True, help="目标法定名或待消歧名称")
    parser.add_argument("--purpose", choices=CONTRACT["enums"]["purpose"], help="全面了解公司用 company_research；未给出时保持待确认")
    parser.add_argument("--enable-scoring", action="store_true",
                        help="仅决策目的可显式启用；发布前仍需确认项目权重和关键维度")
    parser.add_argument("--depth", choices=CONTRACT["enums"]["depth"], default="Standard")
    parser.add_argument("--as-of", help="YYYY-MM-DD；默认使用所选时区的当前日期")
    parser.add_argument("--timezone", default="Asia/Shanghai")
    parser.add_argument("--registration-id", default="")
    parser.add_argument("--geography", default="")
    parser.add_argument("--listing-status", choices=CONTRACT["enums"]["listing"], default="unknown")
    parser.add_argument("--exchange", default="")
    parser.add_argument("--security-code", default="")
    print(dumps(initialize(**vars(parser.parse_args()))), end="")


if __name__ == "__main__":
    raise SystemExit(cli(main))
