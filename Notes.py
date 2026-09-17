import customtkinter as ctk
import json
import os
import queue
import threading
from datetime import datetime
from tkinter import filedialog, messagebox

import requests

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    pystray = None

try:
    import keyboard
except ImportError:
    keyboard = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "notes_client_config.json")

POLL_INTERVAL_MS = 4000
SAVE_DEBOUNCE_MS = 600
HOTKEY_SHOW = "ctrl+alt+n"
HOTKEY_NEW = "ctrl+alt+shift+n"

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"server_url": "", "cert_path": ""}


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def fmt_time(iso):
    if not iso:
        return ""
    try:
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is not None:
            dt = dt.astimezone()
        return dt.strftime("%Y/%m/%d %H:%M")
    except (ValueError, TypeError):
        return ""


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, config_data):
        super().__init__(master)
        self.title("設定同步伺服器")
        self.geometry("440x260")
        self.resizable(False, False)
        self.result = None

        pad = {"padx": 18, "pady": (14, 4)}

        ctk.CTkLabel(self, text="伺服器位址（例如 https://192.168.1.50:5678）").pack(anchor="w", **pad)
        self.url_entry = ctk.CTkEntry(self)
        self.url_entry.pack(fill="x", padx=18)
        self.url_entry.insert(0, config_data.get("server_url", ""))

        ctk.CTkLabel(self, text="伺服器憑證檔（從伺服器複製過來的 cert.pem）").pack(anchor="w", **pad)
        cert_row = ctk.CTkFrame(self, fg_color="transparent")
        cert_row.pack(fill="x", padx=18)
        self.cert_entry = ctk.CTkEntry(cert_row)
        self.cert_entry.pack(side="left", fill="x", expand=True)
        self.cert_entry.insert(0, config_data.get("cert_path", ""))
        ctk.CTkButton(cert_row, text="瀏覽...", width=70, command=self._browse).pack(side="left", padx=(6, 0))

        ctk.CTkLabel(
            self,
            text="伺服器啟動時會印出憑證路徑，把該檔案（certs/cert.pem）\n複製到這台電腦後在此選取。",
            text_color="gray",
            font=ctk.CTkFont(size=11),
            justify="left",
        ).pack(anchor="w", padx=18, pady=(6, 0))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=16, side="bottom")
        ctk.CTkButton(btn_row, text="儲存", command=self._save).pack(side="right")
        ctk.CTkButton(btn_row, text="取消", fg_color="gray40", hover_color="gray30",
                      command=self.destroy).pack(side="right", padx=(0, 8))

        self.transient(master)
        self.grab_set()
        self.wait_window(self)

    def _browse(self):
        path = filedialog.askopenfilename(
            title="選擇 cert.pem", filetypes=[("PEM 憑證", "*.pem"), ("所有檔案", "*.*")]
        )
        if path:
            self.cert_entry.delete(0, "end")
            self.cert_entry.insert(0, path)

    def _save(self):
        self.result = {
            "server_url": self.url_entry.get().strip().rstrip("/"),
            "cert_path": self.cert_entry.get().strip(),
        }
        self.destroy()


class NotesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("記事本")
        self.geometry("900x600")
        self.minsize(700, 450)

        self.config_data = load_config()
        self.notes = []
        self.selected_id = None
        self.editing = False
        self._save_after_id = None
        self.ui_queue = queue.Queue()
        self.tray_icon = None

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_editor()

        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)
        self.after(100, self._drain_queue)

        if not self.config_data.get("server_url"):
            self.after(200, self.open_settings)
        else:
            self.after(200, self.poll_server)

        self._start_tray()
        self._start_hotkeys()

    # ---------- 伺服器連線設定 ----------
    def api_base(self):
        url = self.config_data.get("server_url", "").rstrip("/")
        return f"{url}/api/notes" if url else ""

    def open_settings(self):
        dialog = SettingsDialog(self, self.config_data)
        if dialog.result and dialog.result["server_url"]:
            self.config_data.update(dialog.result)
            save_config(self.config_data)
            self.set_sync_state(None, "設定完成，同步中...")
            self.poll_server()
        elif not self.config_data.get("server_url"):
            self.set_sync_state(False, "尚未設定伺服器")

    def _verify_arg(self):
        cert_path = self.config_data.get("cert_path")
        if cert_path and os.path.exists(cert_path):
            return cert_path
        return True

    # ---------- 左側：搜尋 + 筆記列表 ----------
    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_rowconfigure(2, weight=1)
        sidebar.grid_propagate(False)

        top_bar = ctk.CTkFrame(sidebar, fg_color="transparent")
        top_bar.pack(fill="x", padx=12, pady=(12, 2))
        name_col = ctk.CTkFrame(top_bar, fg_color="transparent")
        name_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(name_col, text="我的記事本", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")

        status_row = ctk.CTkFrame(name_col, fg_color="transparent")
        status_row.pack(anchor="w")
        self.sync_dot = ctk.CTkFrame(status_row, width=8, height=8, corner_radius=4, fg_color="gray")
        self.sync_dot.pack(side="left", pady=2)
        self.sync_dot.pack_propagate(False)
        self.sync_label = ctk.CTkLabel(status_row, text="尚未連線", font=ctk.CTkFont(size=11), text_color="gray")
        self.sync_label.pack(side="left", padx=(5, 0))

        btns = ctk.CTkFrame(top_bar, fg_color="transparent")
        btns.pack(side="right")
        ctk.CTkButton(btns, text="⚙", width=30, command=self.open_settings).pack(side="left", padx=(0, 6))
        ctk.CTkButton(btns, text="＋ 新增", width=70, command=self.new_note).pack(side="left")

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_list())
        search_entry = ctk.CTkEntry(sidebar, placeholder_text="搜尋筆記...", textvariable=self.search_var)
        search_entry.pack(fill="x", padx=12, pady=(8, 8))

        self.list_frame = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))

    # ---------- 右側：編輯區 ----------
    def _build_editor(self):
        editor = ctk.CTkFrame(self, corner_radius=0)
        editor.grid(row=0, column=1, sticky="nswe")
        editor.grid_rowconfigure(2, weight=1)
        editor.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(editor, fg_color="transparent")
        header.grid(row=0, column=0, sticky="we", padx=20, pady=(20, 6))
        header.grid_columnconfigure(0, weight=1)

        self.title_entry = ctk.CTkEntry(header, placeholder_text="標題", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_entry.grid(row=0, column=0, sticky="we")
        self.title_entry.bind("<KeyRelease>", self.schedule_save)

        self.pin_btn = ctk.CTkButton(header, text="☆ 置頂", width=80, command=self.toggle_pin)
        self.pin_btn.grid(row=0, column=1, padx=(8, 0))

        meta_row = ctk.CTkFrame(editor, fg_color="transparent")
        meta_row.grid(row=1, column=0, sticky="we", padx=20)
        self.save_dot = ctk.CTkFrame(meta_row, width=8, height=8, corner_radius=4, fg_color="gray")
        self.save_dot.pack(side="left", pady=2)
        self.save_dot.pack_propagate(False)
        self.meta_label = ctk.CTkLabel(meta_row, text="", text_color="gray", font=ctk.CTkFont(size=12))
        self.meta_label.pack(side="left", padx=(6, 0))

        self.content_box = ctk.CTkTextbox(editor, font=ctk.CTkFont(size=14), wrap="word")
        self.content_box.grid(row=2, column=0, sticky="nswe", padx=20, pady=10)
        self.content_box.bind("<KeyRelease>", self.schedule_save)

        btn_bar = ctk.CTkFrame(editor, fg_color="transparent")
        btn_bar.grid(row=3, column=0, sticky="we", padx=20, pady=(0, 20))
        ctk.CTkButton(btn_bar, text="刪除", fg_color="#c0392b", hover_color="#922b21",
                      command=self.delete_current).pack(side="left")

        self.set_editor_enabled(False)

    # ---------- 跨執行緒佇列 ----------
    def _drain_queue(self):
        try:
            while True:
                action = self.ui_queue.get_nowait()
                action()
        except queue.Empty:
            pass
        self.after(100, self._drain_queue)

    def set_sync_state(self, online, label=None):
        if online is True:
            self.sync_dot.configure(fg_color="#2f8f6f")
            self.sync_label.configure(text=label or "已同步", text_color="#2f8f6f")
        elif online is False:
            self.sync_dot.configure(fg_color="#c8842a")
            self.sync_label.configure(text=label or "離線", text_color="#c8842a")
        else:
            self.sync_dot.configure(fg_color="gray")
            self.sync_label.configure(text=label or "連線中...", text_color="gray")

    # ---------- 伺服器同步 ----------
    def poll_server(self):
        if not self.api_base():
            return
        api = self.api_base()

        def worker():
            try:
                r = requests.get(api, timeout=5, verify=self._verify_arg())
                r.raise_for_status()
                data = r.json()
                self.ui_queue.put(lambda: self._apply_server_notes(data))
            except requests.RequestException:
                self.ui_queue.put(lambda: self.set_sync_state(False))

        threading.Thread(target=worker, daemon=True).start()
        self.after(POLL_INTERVAL_MS, self.poll_server)

    def _apply_server_notes(self, data):
        self.set_sync_state(True)
        if self.editing and self.selected_id:
            local = self._find(self.selected_id)
            if local:
                for n in data:
                    if n["id"] == self.selected_id:
                        n["title"] = local["title"]
                        n["content"] = local["content"]
        self.notes = data
        self.refresh_list()

    # ---------- 資料操作 ----------
    def refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        keyword = self.search_var.get().strip().lower()
        filtered = [
            n for n in self.notes
            if keyword in n["title"].lower() or keyword in n["content"].lower()
        ] if keyword else list(self.notes)

        filtered.sort(key=lambda n: n["updated_at"], reverse=True)
        filtered.sort(key=lambda n: n.get("pinned", False), reverse=True)

        if not filtered:
            msg = "沒有筆記" if self.notes else "還沒有筆記，點右上角新增第一篇吧"
            ctk.CTkLabel(self.list_frame, text=msg, text_color="gray").pack(pady=20)
            return

        for note in filtered:
            self._build_list_item(note)

    def _build_list_item(self, note):
        selected = note["id"] == self.selected_id
        item = ctk.CTkFrame(
            self.list_frame,
            corner_radius=8,
            fg_color=("#dbeee0", "#274031") if selected else "transparent",
        )
        item.pack(fill="x", pady=2, padx=2)

        title = note["title"] or "(無標題)"
        if note.get("pinned"):
            title = "📌 " + title

        preview = note["content"].strip().splitlines()
        preview_text = preview[0][:40] if preview else ""
        time_text = fmt_time(note["updated_at"])

        label = ctk.CTkLabel(
            item, text=title, anchor="w", font=ctk.CTkFont(size=14, weight="bold"), justify="left"
        )
        label.pack(fill="x", padx=10, pady=(8, 0))

        sub = ctk.CTkLabel(
            item, text=f"{preview_text}\n{time_text}", anchor="w", justify="left",
            text_color="gray", font=ctk.CTkFont(size=11)
        )
        sub.pack(fill="x", padx=10, pady=(0, 8))

        for widget in (item, label, sub):
            widget.bind("<Button-1>", lambda e, nid=note["id"]: self.select_note(nid))

    def select_note(self, note_id):
        self.editing = False
        self.selected_id = note_id
        note = self._find(note_id)
        if not note:
            return

        self.set_editor_enabled(True)
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, note["title"])
        self.content_box.delete("1.0", "end")
        self.content_box.insert("1.0", note["content"])
        self.pin_btn.configure(text="★ 已置頂" if note.get("pinned") else "☆ 置頂")
        self.meta_label.configure(text=f'建立於 {fmt_time(note["created_at"])}')
        self.save_dot.configure(fg_color="#2f8f6f")
        self.refresh_list()

    def new_note(self):
        if not self.api_base():
            self.open_settings()
            return
        api = self.api_base()

        def worker():
            try:
                r = requests.post(api, json={"title": "", "content": ""}, timeout=5, verify=self._verify_arg())
                r.raise_for_status()
                note = r.json()
                self.ui_queue.put(lambda: self._on_note_created(note))
            except requests.RequestException:
                self.ui_queue.put(lambda: self.set_sync_state(False))

        threading.Thread(target=worker, daemon=True).start()

    def _on_note_created(self, note):
        self.set_sync_state(True)
        self.notes.insert(0, note)
        self.select_note(note["id"])
        self.title_entry.focus_set()

    def schedule_save(self, event=None):
        if self.selected_id is None:
            return
        self.editing = True
        self.save_dot.configure(fg_color="gray")
        if self._save_after_id:
            self.after_cancel(self._save_after_id)
        self._save_after_id = self.after(SAVE_DEBOUNCE_MS, self.commit_edits)

    def commit_edits(self):
        self._save_after_id = None
        note = self._find(self.selected_id)
        if not note or not self.api_base():
            return
        note_id = note["id"]
        title = self.title_entry.get()
        content = self.content_box.get("1.0", "end-1c")
        api = self.api_base()

        def worker():
            try:
                r = requests.put(
                    f"{api}/{note_id}", json={"title": title, "content": content},
                    timeout=5, verify=self._verify_arg(),
                )
                r.raise_for_status()
                updated = r.json()
                self.ui_queue.put(lambda: self._on_note_saved(updated))
            except requests.RequestException:
                self.ui_queue.put(lambda: self.set_sync_state(False))

        threading.Thread(target=worker, daemon=True).start()

    def _on_note_saved(self, updated):
        self.set_sync_state(True)
        note = self._find(updated["id"])
        if note:
            note.update(updated)
        self.editing = False
        if self.selected_id == updated["id"]:
            self.save_dot.configure(fg_color="#2f8f6f")
        self.refresh_list()

    def delete_current(self):
        if self.selected_id is None:
            return
        if not messagebox.askyesno("刪除筆記", "確定要刪除這篇筆記嗎？"):
            return
        note_id = self.selected_id
        api = self.api_base()

        def worker():
            if api:
                try:
                    requests.delete(f"{api}/{note_id}", timeout=5, verify=self._verify_arg())
                except requests.RequestException:
                    pass
            self.ui_queue.put(lambda: self._on_note_deleted(note_id))

        threading.Thread(target=worker, daemon=True).start()

    def _on_note_deleted(self, note_id):
        self.notes = [n for n in self.notes if n["id"] != note_id]
        if self.selected_id == note_id:
            self.selected_id = None
            self.editing = False
            self.set_editor_enabled(False)
            self.title_entry.delete(0, "end")
            self.content_box.delete("1.0", "end")
            self.meta_label.configure(text="")
        self.refresh_list()

    def toggle_pin(self):
        note = self._find(self.selected_id)
        if not note or not self.api_base():
            return
        note_id = note["id"]
        api = self.api_base()

        def worker():
            try:
                r = requests.patch(f"{api}/{note_id}/pin", timeout=5, verify=self._verify_arg())
                r.raise_for_status()
                updated = r.json()
                self.ui_queue.put(lambda: self._on_pin_toggled(updated))
            except requests.RequestException:
                self.ui_queue.put(lambda: self.set_sync_state(False))

        threading.Thread(target=worker, daemon=True).start()

    def _on_pin_toggled(self, updated):
        self.set_sync_state(True)
        note = self._find(updated["id"])
        if note:
            note.update(updated)
        if self.selected_id == updated["id"]:
            self.pin_btn.configure(text="★ 已置頂" if updated["pinned"] else "☆ 置頂")
        self.refresh_list()

    def _find(self, note_id):
        return next((n for n in self.notes if n["id"] == note_id), None)

    def set_editor_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.title_entry.configure(state=state)
        self.content_box.configure(state=state)
        self.pin_btn.configure(state=state)

    # ---------- 系統匣 ----------
    def _tray_image(self):
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([4, 4, size - 4, size - 4], radius=14, fill=(47, 143, 111, 255))
        draw.rectangle([18, 20, 46, 24], fill=(255, 255, 255, 230))
        draw.rectangle([18, 30, 46, 34], fill=(255, 255, 255, 230))
        draw.rectangle([18, 40, 38, 44], fill=(255, 255, 255, 230))
        return img

    def _start_tray(self):
        if pystray is None:
            return
        menu = pystray.Menu(
            pystray.MenuItem("開啟主視窗", self._tray_show, default=True),
            pystray.MenuItem("新增筆記", self._tray_new),
            pystray.MenuItem("結束", self._tray_quit),
        )
        self.tray_icon = pystray.Icon("notes_app", self._tray_image(), "記事本", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _tray_show(self, icon=None, item=None):
        self.ui_queue.put(self.show_window)

    def _tray_new(self, icon=None, item=None):
        self.ui_queue.put(self.show_window)
        self.ui_queue.put(self.new_note)

    def _tray_quit(self, icon=None, item=None):
        self.ui_queue.put(self.quit_app)

    def show_window(self):
        self.deiconify()
        self.state("normal")
        self.lift()
        self.focus_force()

    def hide_to_tray(self):
        if self.tray_icon is None:
            if messagebox.askyesno("結束", "未啟用系統匣，是否直接結束程式？"):
                self.quit_app()
            return
        self.withdraw()

    def quit_app(self):
        if keyboard is not None:
            try:
                keyboard.unhook_all_hotkeys()
            except Exception:
                pass
        if self.tray_icon is not None:
            self.tray_icon.stop()
        self.destroy()

    # ---------- 全域快捷鍵 ----------
    def _start_hotkeys(self):
        if keyboard is None:
            return
        try:
            keyboard.add_hotkey(HOTKEY_SHOW, lambda: self.ui_queue.put(self.show_window))
            keyboard.add_hotkey(HOTKEY_NEW, self._hotkey_new_note)
        except Exception:
            pass

    def _hotkey_new_note(self):
        self.ui_queue.put(self.show_window)
        self.ui_queue.put(self.new_note)


def main():
    app = NotesApp()
    app.mainloop()


if __name__ == "__main__":
    main()
