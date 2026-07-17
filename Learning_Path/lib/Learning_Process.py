"""學習進度平台核心邏輯：排程產生、進度存取、Markdown 匯出。

供 websites/backend（網站）與未來手機介面共用的 Library(庫)。
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

subject = ["微積分", "英文", "工程數學", "程式語言"]  # 學習科目

TOTAL_STAGES = 10  # 十個進度
STAGE_HOURS = 2  # 每個進度為兩小時進行
TOTAL_DAYS = 20  # 一共採用20天進行
DAY_STEP = TOTAL_DAYS // TOTAL_STAGES  # 每個進度間隔天數

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "progress.json"

STATUS_PENDING = "pending"
STATUS_ACTIVE = "active"
STATUS_DONE = "done"


@dataclass
class Stage:
    id: int
    day: int
    date: str
    subject: str
    hours: int
    status: str = STATUS_PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


def generate_plan(start_date: Optional[date] = None) -> list[Stage]:
    """產生 10 個進度、每個 2 小時、間隔 2 天、共 20 天的學習排程，科目輪替。"""
    start_date = start_date or date.today()
    stages = []
    for i in range(TOTAL_STAGES):
        day_offset = i * DAY_STEP
        stage_date = start_date + timedelta(days=day_offset)
        stages.append(
            Stage(
                id=i + 1,
                day=day_offset + 1,
                date=stage_date.isoformat(),
                subject=subject[i % len(subject)],
                hours=STAGE_HOURS,
            )
        )
    return stages


def load_process(path: Path = DATA_FILE) -> list[Stage]:
    """讀取已儲存的學習進度；若尚未存在則產生新排程並存檔。"""
    if path.exists():
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [Stage(**item) for item in raw]
    stages = generate_plan()
    save_process(stages, path)
    return stages


def save_process(stages: list[Stage], path: Path = DATA_FILE) -> None:
    """儲存學習進度到 JSON 檔案。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([asdict(s) for s in stages], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _find(stages: list[Stage], stage_id: int) -> Stage:
    for s in stages:
        if s.id == stage_id:
            return s
    raise ValueError(f"找不到進度 id={stage_id}")


def start_stage(stages: list[Stage], stage_id: int) -> Stage:
    stage = _find(stages, stage_id)
    stage.status = STATUS_ACTIVE
    stage.started_at = datetime.now().isoformat(timespec="seconds")
    return stage


def complete_stage(stages: list[Stage], stage_id: int) -> Stage:
    stage = _find(stages, stage_id)
    stage.status = STATUS_DONE
    stage.completed_at = datetime.now().isoformat(timespec="seconds")
    return stage


def progress_summary(stages: list[Stage]) -> dict:
    done = sum(1 for s in stages if s.status == STATUS_DONE)
    total = len(stages)
    current = next((s for s in stages if s.status != STATUS_DONE), None)
    return {
        "done": done,
        "total": total,
        "percent": round(done / total * 100, 1) if total else 0.0,
        "current_stage": current.id if current else None,
    }


def export_markdown(stages: list[Stage]) -> str:
    """輸出成 markdown 檔案格式的學習進度報告。"""
    summary = progress_summary(stages)
    status_label = {STATUS_PENDING: "未開始", STATUS_ACTIVE: "進行中", STATUS_DONE: "已完成"}
    lines = [
        "# 學習進度報告",
        "",
        f"完成度：{summary['done']}/{summary['total']}（{summary['percent']}%）",
        "",
        "| 進度 | 天數 | 日期 | 科目 | 時數 | 狀態 |",
        "|---|---|---|---|---|---|",
    ]
    for s in stages:
        lines.append(
            f"| {s.id} | Day {s.day} | {s.date} | {s.subject} | {s.hours}h | {status_label[s.status]} |"
        )
    return "\n".join(lines)
