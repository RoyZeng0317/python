"""MP4 影片壓縮小工具：呼叫系統 ffmpeg，依品質等級或目標檔案大小壓縮單一檔案或整個資料夾。

支援兩種介面：
  - CLI：python mp4zip.py <檔案或資料夾路徑> [-q 低|中|高 | -s 目標MB] [-o 輸出資料夾]
  - GUI：不帶參數直接執行 `python mp4zip.py` 即會開啟視窗
"""

from __future__ import annotations

import argparse, shutil, subprocess, sys, threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

if sys.stdout.encoding.lower() != "utf-8":  # Windows 主控台預設編碼易造成中文亂碼
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

QUALITY_CRF = {"低": 20, "中": 26, "高": 32}  # CRF 越大壓縮率越高、畫質越低、檔案越小
BG_COLOR, PANEL_BG, FG_COLOR = "#1e1e1e", "#252526", "#ffffff"
ACCENT_BG, ACCENT_ACTIVE = "#0e639c", "#1177bb"


def collect_mp4s(path: Path) -> list[Path]:
    """輸入單一檔案就回傳自己，輸入資料夾就遞迴找出底下所有 mp4。"""
    return [path] if path.is_file() else sorted(path.rglob("*.mp4"))


def output_path(src: Path, out_dir: Path | None) -> Path:
    return (out_dir or src.parent) / f"{src.stem}_compressed.mp4"


def compress_video(src: Path, dst: Path, crf: int) -> None:
    """呼叫系統 ffmpeg 壓縮單一 mp4 檔案（H.264 + AAC）。"""
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-vcodec", "libx264", "-crf", str(crf), "-preset", "medium", "-pix_fmt", "yuv420p",
        "-acodec", "aac", "-b:a", "128k", "-movflags", "+faststart", str(dst),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def probe_duration(path: Path) -> float:
    """用 ffprobe 讀取影片總秒數。"""
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]
    out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip()
    return float(out)


def compress_to_size(src: Path, dst: Path, target_mb: float, audio_kbps: int = 128) -> None:
    """兩階段編碼（2-pass），依影片長度回推 bitrate，把影片壓到指定 MB 以下。"""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.stat().st_size <= target_mb * 1024 * 1024:  # 原檔已小於目標，直接複製即可
        shutil.copyfile(src, dst)
        return
    duration = probe_duration(src)
    total_kbps = target_mb * 8192 / duration * 0.98  # 抓 2% 安全餘量避免超出目標
    video_kbps = max(int(total_kbps - audio_kbps), 100)  # 保留可看的最低畫質下限

    passlog = dst.parent / f"{src.stem}_2pass"
    null_out = "NUL" if sys.platform == "win32" else "/dev/null"
    base = [
        "ffmpeg", "-y", "-i", str(src),
        "-vcodec", "libx264", "-b:v", f"{video_kbps}k", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-passlogfile", str(passlog),
    ]
    try:
        subprocess.run(base + ["-pass", "1", "-an", "-f", "mp4", null_out], check=True, capture_output=True, text=True)
        subprocess.run(
            base + ["-pass", "2", "-acodec", "aac", "-b:a", f"{audio_kbps}k", "-movflags", "+faststart", str(dst)],
            check=True, capture_output=True, text=True,
        )
    finally:
        for log in dst.parent.glob(f"{src.stem}_2pass*"):
            log.unlink(missing_ok=True)


# ---------- CLI ----------

def run_cli(args: argparse.Namespace) -> None:
    src_path = Path(args.input)
    if not src_path.exists():
        sys.exit(f"找不到路徑: {src_path}")

    files = collect_mp4s(src_path)
    if not files:
        sys.exit("找不到任何 mp4 檔案")

    out_dir = Path(args.output) if args.output else None
    for i, f in enumerate(files, 1):
        dst = output_path(f, out_dir)
        print(f"[{i}/{len(files)}] 壓縮中: {f.name}")
        try:
            if args.size_mb:
                compress_to_size(f, dst, args.size_mb)
            else:
                compress_video(f, dst, QUALITY_CRF[args.quality])
        except subprocess.CalledProcessError as e:
            last_line = e.stderr.strip().splitlines()[-1] if e.stderr else str(e)
            print(f"  失敗: {last_line}")
            continue
        before, after = f.stat().st_size, dst.stat().st_size
        print(f"  完成: {before / 1e6:.1f}MB -> {after / 1e6:.1f}MB")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MP4 影片壓縮小工具")
    parser.add_argument("input", nargs="?", help="mp4 檔案或資料夾路徑（留空啟動 GUI）")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("-q", "--quality", choices=list(QUALITY_CRF), default="中", help="壓縮品質等級")
    mode.add_argument("-s", "--size-mb", type=float, help="壓縮到指定大小以下（MB），例如 -s 25")
    parser.add_argument("-o", "--output", help="輸出資料夾（預設與原檔同資料夾）")
    return parser


# ---------- GUI ----------

class CompressorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("MP4 影片壓縮小工具")
        self.configure(bg=BG_COLOR)
        self.geometry("560x480")

        self.input_path: Path | None = None
        self.output_dir: Path | None = None
        self.quality = tk.StringVar(value="中")
        self.use_size_limit = tk.BooleanVar(value=False)
        self.size_mb = tk.StringVar(value="25")

        self._build_ui()

    def _build_ui(self) -> None:
        PADX, PADY = 12, 6

        self.path_label = tk.Label(
            self, text="尚未選擇檔案或資料夾", bg=BG_COLOR, fg=FG_COLOR, anchor="w", wraplength=520,
        )
        self.path_label.pack(fill="x", padx=PADX, pady=PADY)

        btn_row = tk.Frame(self, bg=BG_COLOR)
        btn_row.pack(fill="x", padx=PADX, pady=PADY)
        tk.Button(
            btn_row, text="選擇檔案", command=self.pick_file,
            bg=ACCENT_BG, fg=FG_COLOR, activebackground=ACCENT_ACTIVE, relief="flat",
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            btn_row, text="選擇資料夾", command=self.pick_folder,
            bg=ACCENT_BG, fg=FG_COLOR, activebackground=ACCENT_ACTIVE, relief="flat",
        ).pack(side="left")

        quality_row = tk.Frame(self, bg=BG_COLOR)
        quality_row.pack(fill="x", padx=PADX, pady=PADY)
        tk.Label(quality_row, text="壓縮品質:", bg=BG_COLOR, fg=FG_COLOR).pack(side="left")
        for q in QUALITY_CRF:
            tk.Radiobutton(
                quality_row, text=f"{q}壓縮", variable=self.quality, value=q,
                bg=BG_COLOR, fg=FG_COLOR, selectcolor=PANEL_BG,
                activebackground=BG_COLOR, activeforeground=FG_COLOR,
            ).pack(side="left", padx=4)

        size_row = tk.Frame(self, bg=BG_COLOR)
        size_row.pack(fill="x", padx=PADX, pady=PADY)
        tk.Checkbutton(
            size_row, text="改為壓到指定大小以下:", variable=self.use_size_limit,
            bg=BG_COLOR, fg=FG_COLOR, selectcolor=PANEL_BG,
            activebackground=BG_COLOR, activeforeground=FG_COLOR,
        ).pack(side="left")
        tk.Entry(size_row, textvariable=self.size_mb, width=6, bg=PANEL_BG, fg=FG_COLOR, insertbackground=FG_COLOR).pack(side="left", padx=4)
        tk.Label(size_row, text="MB", bg=BG_COLOR, fg=FG_COLOR).pack(side="left")

        self.run_btn = tk.Button(
            self, text="開始壓縮", command=self.start_compress,
            bg=ACCENT_BG, fg=FG_COLOR, activebackground=ACCENT_ACTIVE,
            relief="flat", font=("Segoe UI", 12, "bold"),
        )
        self.run_btn.pack(fill="x", padx=PADX, pady=PADY)

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill="x", padx=PADX, pady=PADY)

        self.log = tk.Text(self, bg=PANEL_BG, fg=FG_COLOR, height=14, state="disabled")
        self.log.pack(fill="both", expand=True, padx=PADX, pady=PADY)

    def pick_file(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("MP4 影片", "*.mp4")])
        if path:
            self.input_path = Path(path)
            self.path_label.configure(text=f"檔案: {path}")

    def pick_folder(self) -> None:
        path = filedialog.askdirectory()
        if path:
            self.input_path = Path(path)
            self.path_label.configure(text=f"資料夾: {path}")

    def log_line(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def start_compress(self) -> None:
        if self.input_path is None:
            messagebox.showwarning("提醒", "請先選擇檔案或資料夾")
            return
        files = collect_mp4s(self.input_path)
        if not files:
            messagebox.showwarning("提醒", "找不到任何 mp4 檔案")
            return
        target_mb: float | None = None
        if self.use_size_limit.get():
            try:
                target_mb = float(self.size_mb.get())
                if target_mb <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("提醒", "目標大小請輸入大於 0 的數字")
                return
        self.run_btn.configure(state="disabled")
        self.progress.configure(maximum=len(files), value=0)
        threading.Thread(target=self._compress_worker, args=(files, target_mb), daemon=True).start()

    def _compress_worker(self, files: list[Path], target_mb: float | None) -> None:
        crf = QUALITY_CRF[self.quality.get()]
        for i, f in enumerate(files, 1):
            dst = output_path(f, self.output_dir)
            self.after(0, self.log_line, f"[{i}/{len(files)}] 壓縮中: {f.name}")
            try:
                if target_mb is not None:
                    compress_to_size(f, dst, target_mb)
                else:
                    compress_video(f, dst, crf)
                before, after = f.stat().st_size, dst.stat().st_size
                self.after(0, self.log_line, f"  完成: {before / 1e6:.1f}MB -> {after / 1e6:.1f}MB")
            except subprocess.CalledProcessError:
                self.after(0, self.log_line, f"  失敗: {f.name}")
            self.after(0, self.progress.step, 1)
        self.after(0, lambda: self.run_btn.configure(state="normal"))
        self.after(0, lambda: messagebox.showinfo("完成", "壓縮作業已完成"))


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    if args.input:
        run_cli(args)
    else:
        CompressorApp().mainloop()


if __name__ == "__main__":
    main()
