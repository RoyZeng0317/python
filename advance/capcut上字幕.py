# enivorment
# pip install faster-whisper
from faster_whisper import WhisperModel

m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=8)
segs, _ = m.transcribe(r"C:\Users\Roy\Downloads\reels_uninstall.mp4",
                       language="zh", vad_filter=True)

def ts(t):
    h, r = divmod(t, 3600); mi, s = divmod(r, 60)
    return f"{int(h):02d}:{int(mi):02d}:{s:06.3f}".replace(".", ",")

with open("out.srt", "w", encoding="utf-8") as f:
   for i, s in enumerate(segs, 1):
        f.write(f"{i}\n{ts(s.start)} --> {ts(s.end)}\n{s.text.strip()}\n\n")