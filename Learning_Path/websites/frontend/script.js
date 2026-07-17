const clockEl = document.getElementById("clock");
const stageListEl = document.getElementById("stageList");
const progressFillEl = document.getElementById("progressFill");
const progressTextEl = document.getElementById("progressText");
const focusPanelEl = document.getElementById("focusPanel");
const focusSubjectEl = document.getElementById("focusSubject");
const focusTimerEl = document.getElementById("focusTimer");
const completeBtn = document.getElementById("completeBtn");
const exportBtn = document.getElementById("exportBtn");
const resetBtn = document.getElementById("resetBtn");
const stageCardTpl = document.getElementById("stageCardTpl");

const STATUS_LABEL = { pending: "未開始", active: "進行中", done: "已完成" };

let activeStageId = null;

async function fetchJson(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`${url} -> ${res.status}`);
  return res.json();
}

function formatSeconds(total) {
  const h = String(Math.floor(total / 3600)).padStart(2, "0");
  const m = String(Math.floor((total % 3600) / 60)).padStart(2, "0");
  const s = String(total % 60).padStart(2, "0");
  return `${h}:${m}:${s}`;
}

function renderStages(stages) {
  stageListEl.innerHTML = "";
  stages.forEach((stage) => {
    const node = stageCardTpl.content.cloneNode(true);
    node.querySelector(".stage-id").textContent = `#${stage.id} · Day ${stage.day}`;
    const statusEl = node.querySelector(".stage-status");
    statusEl.textContent = STATUS_LABEL[stage.status];
    statusEl.classList.add(stage.status);
    node.querySelector(".stage-subject").textContent = stage.subject;
    node.querySelector(".stage-meta").textContent = `${stage.date} · ${stage.hours} 小時`;
    const btn = node.querySelector(".start-btn");
    if (stage.status === "done") {
      btn.textContent = "已完成";
      btn.disabled = true;
    } else if (stage.status === "active") {
      btn.textContent = "進行中";
      btn.disabled = true;
    } else {
      btn.addEventListener("click", () => startStage(stage.id));
    }
    stageListEl.appendChild(node);
  });
}

function renderProgress(summary) {
  const percent = summary.percent || 0;
  progressFillEl.style.width = `${percent}%`;
  progressTextEl.textContent = `${summary.done} / ${summary.total} 完成（${percent}%）`;
}

async function loadAll() {
  const [stages, summary] = await Promise.all([
    fetchJson("/api/plan"),
    fetchJson("/api/progress"),
  ]);
  renderStages(stages);
  renderProgress(summary);
  const active = stages.find((s) => s.status === "active");
  activeStageId = active ? active.id : null;
  focusPanelEl.hidden = !active;
  if (active) focusSubjectEl.textContent = `#${active.id} ${active.subject}`;
}

async function startStage(id) {
  await fetchJson(`/api/stage/${id}/start`, { method: "POST" });
  await loadAll();
}

async function completeStage(id) {
  await fetchJson(`/api/stage/${id}/complete`, { method: "POST" });
  activeStageId = null;
  focusPanelEl.hidden = true;
  await loadAll();
}

completeBtn.addEventListener("click", () => {
  if (activeStageId) completeStage(activeStageId);
});

resetBtn.addEventListener("click", async () => {
  if (!confirm("確定要重新產生 20 天排程嗎？目前進度將會被覆蓋。")) return;
  await fetchJson("/api/plan/reset", { method: "POST" });
  await loadAll();
});

exportBtn.addEventListener("click", async () => {
  const res = await fetch("/api/export/markdown");
  const text = await res.text();
  const blob = new Blob([text], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "learning-progress.md";
  a.click();
  URL.revokeObjectURL(url);
});

async function tickClock() {
  try {
    const data = await fetchJson("/api/clock");
    clockEl.textContent = new Date(data.now).toLocaleTimeString("zh-TW", { hour12: false });
    if (data.session) {
      focusTimerEl.textContent = data.session.finished
        ? "00:00:00"
        : formatSeconds(data.session.remaining_seconds);
    }
  } catch (err) {
    clockEl.textContent = "連線中斷";
  }
}

loadAll();
tickClock();
setInterval(tickClock, 1000);
