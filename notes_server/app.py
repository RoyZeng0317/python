import json
import os
import threading
import uuid
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_from_directory

from tls import ensure_cert

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "notes_data.json")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=None)
_lock = threading.Lock()


def _now():
    return datetime.now(timezone.utc).isoformat()


def _load():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save(notes):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    tmp_path = DATA_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, DATA_FILE)


def _find(notes, note_id):
    return next((n for n in notes if n["id"] == note_id), None)


@app.get("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.get("/api/notes")
def list_notes():
    with _lock:
        notes = _load()
    return jsonify(notes)


@app.post("/api/notes")
def create_note():
    payload = request.get_json(silent=True) or {}
    now = _now()
    note = {
        "id": uuid.uuid4().hex,
        "title": str(payload.get("title", "")),
        "content": str(payload.get("content", "")),
        "pinned": False,
        "created_at": now,
        "updated_at": now,
    }
    with _lock:
        notes = _load()
        notes.append(note)
        _save(notes)
    return jsonify(note), 201


@app.put("/api/notes/<note_id>")
def update_note(note_id):
    payload = request.get_json(silent=True) or {}
    with _lock:
        notes = _load()
        note = _find(notes, note_id)
        if note is None:
            return jsonify({"error": "not found"}), 404
        if "title" in payload:
            note["title"] = str(payload["title"])
        if "content" in payload:
            note["content"] = str(payload["content"])
        note["updated_at"] = _now()
        _save(notes)
    return jsonify(note)


@app.patch("/api/notes/<note_id>/pin")
def toggle_pin(note_id):
    with _lock:
        notes = _load()
        note = _find(notes, note_id)
        if note is None:
            return jsonify({"error": "not found"}), 404
        note["pinned"] = not note.get("pinned", False)
        note["updated_at"] = _now()
        _save(notes)
    return jsonify(note)


@app.delete("/api/notes/<note_id>")
def delete_note(note_id):
    with _lock:
        notes = _load()
        if _find(notes, note_id) is None:
            return jsonify({"error": "not found"}), 404
        notes = [n for n in notes if n["id"] != note_id]
        _save(notes)
    return "", 204


if __name__ == "__main__":
    cert_path, key_path = ensure_cert()
    print(f"TLS 憑證: {cert_path}")
    print("請把這個檔案複製到桌面用戶端，並在設定（⚙）中指向它。")
    app.run(host="0.0.0.0", port=5678, threaded=True, ssl_context=(cert_path, key_path))
