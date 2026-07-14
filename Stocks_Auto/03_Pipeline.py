"""M2-M7 端到端管線入口點。
依 PLAN.md：擷取(M2) -> rules.md規則篩選(M3) -> 去重(M4) -> 分組(M5) ->
摘要/關鍵字(M6) -> 輸出JSON(M7)。

各來源擷取器彼此獨立，任一來源失敗（HTML結構變更/被擋/連線錯誤等）僅記錄
訊息並回傳空清單，不會讓整條管線崩潰（見各 fetch_*.py 內的例外處理）。

執行方式：
    .venv\\Scripts\\python.exe 03_Pipeline.py
"""
import datetime

import config
import rules
import dedup
import grouping
import summarize
import output

import fetch_cnyes
import fetch_ctee
import fetch_ptt
import fetch_udn
import fetch_youtube


def _fetch_yahoo():
    import importlib

    yahoo_module = importlib.import_module("02_Fetch_Yahoo")
    return yahoo_module.fetch()


def fetch_all():
    """依序呼叫每個來源的 fetch()，個別失敗不影響其他來源。"""
    all_articles = []
    fetch_funcs = {
        "yahoo": _fetch_yahoo,
        "cnyes": fetch_cnyes.fetch,
        "udn": fetch_udn.fetch,
        "ctee": fetch_ctee.fetch,
        "ptt": fetch_ptt.fetch,
        "youtube": fetch_youtube.fetch,
    }
    for name, fetch_func in fetch_funcs.items():
        try:
            articles = fetch_func()
        except Exception as exc:
            print(f"[pipeline] 來源 {name} 擷取時發生未預期例外，略過：{type(exc).__name__}: {exc}")
            articles = []
        print(f"[pipeline] {name}: 擷取 {len(articles)} 篇")
        all_articles.extend(articles)
    return all_articles


def run():
    today = datetime.date.today()
    print(f"=== Stocks_Auto pipeline 開始執行 {today.isoformat()} ===")

    raw_articles = fetch_all()
    print(f"[pipeline] 共擷取 {len(raw_articles)} 篇（去重/篩選前）")

    filtered = rules.apply_rules(raw_articles, today=today)
    print(f"[pipeline] rules.md 篩選後剩 {len(filtered)} 篇")

    deduped = dedup.dedup(filtered)
    print(f"[pipeline] 去重後剩 {len(deduped)} 篇")

    grouped = grouping.group(deduped)
    print(f"[pipeline] 分為 {len(grouped)} 組")

    summarized = summarize.summarize_groups(grouped)

    report = output.build_report(summarized, report_date=today)
    path = output.write_report(report)
    print(f"[pipeline] 已輸出：{path}")
    print(f"=== 完成，共 {report['total_articles']} 篇、{report['group_count']} 組 ===")
    return path


if __name__ == "__main__":
    run()
