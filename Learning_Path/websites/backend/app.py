"""學習進度平台後端 API（FastAPI）。同時掛載前端靜態檔，網站與手機瀏覽器共用同一個 responsive 介面。"""
from __future__ import annotations

import os
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # Learning_Path/
sys.path.insert(0, str(ROOT / "lib"))

import Learning_Process as lp  # noqa: E402
import 專注時鐘 as clock_lib  # noqa: E402

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import PlainTextResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

app = FastAPI(title="學習進度平台 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

focus_clock = clock_lib.FocusClock()
stages = lp.load_process()


def _save() -> None:
    lp.save_process(stages)


@app.get("/api/health")
def health():
    return {"ok": True, "time": clock_lib.FocusClock.now()}


@app.get("/api/clock")
def get_clock():
    session = focus_clock.session
    data = {"now": clock_lib.FocusClock.now(), "session": None}
    if session:
        data["session"] = {
            "stage_id": session.stage_id,
            "remaining_seconds": session.remaining_seconds(),
            "finished": session.is_finished(),
        }
    return data


@app.get("/api/plan")
def get_plan():
    return [asdict(s) for s in stages]


@app.get("/api/progress")
def get_progress():
    return lp.progress_summary(stages)


@app.post("/api/stage/{stage_id}/start")
def api_start_stage(stage_id: int):
    try:
        stage = lp.start_stage(stages, stage_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    focus_clock.start(stage_id, duration_minutes=stage.hours * 60)
    _save()
    return asdict(stage)


@app.post("/api/stage/{stage_id}/complete")
def api_complete_stage(stage_id: int):
    try:
        stage = lp.complete_stage(stages, stage_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    if focus_clock.session and focus_clock.session.stage_id == stage_id:
        focus_clock.stop()
    _save()
    return asdict(stage)


@app.post("/api/plan/reset")
def reset_plan():
    global stages
    stages = lp.generate_plan()
    focus_clock.stop()
    _save()
    return [asdict(s) for s in stages]


@app.get("/api/export/markdown", response_class=PlainTextResponse)
def export_markdown():
    return lp.export_markdown(stages)


FRONTEND_DIR = ROOT / "websites" / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
