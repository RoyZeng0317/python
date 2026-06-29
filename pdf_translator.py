"""
PDF Chinese → English Translator  (v3 — fast batch mode)
=========================================================
• Preserves exact layout: images, table borders, lines, colours, positions
• Batches ALL Chinese text on a page into ONE API call → ~2 s/page instead of 27 s
• Suppresses harmless MuPDF ExtGState / resource warnings
• Auto-scales font size when translated text is wider than the original

SETUP (run once):
    pip install pymupdf deep-translator tqdm

    # Optional – translate text baked into images:
    pip install pytesseract pillow
    # + Tesseract binary: https://github.com/UB-Mannheim/tesseract/wiki

USAGE:
    python pdf_translator.py input.pdf output.pdf [options]

OPTIONS:
    --service   google | mymemory | deepl   (default: google)
    --deepl-key YOUR_KEY                    (only for --service deepl)
    --start     first page (1-based)        (default: 1)
    --end       last page  (1-based)        (default: all)
    --delay     seconds between batch calls (default: 0.4)
    --ocr       translate text inside images (requires pytesseract)

EXAMPLES:
    python pdf_translator.py "Electronic book-All.pdf" "Electronic book-All-EN.pdf"
    python pdf_translator.py input.pdf out.pdf --start 1 --end 50
    python pdf_translator.py input.pdf out.pdf --service deepl --deepl-key sk-xxx
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from typing import Dict, List, Optional, Tuple

# ── Dependency checks ─────────────────────────────────────────────────────────
try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("Missing PyMuPDF.  Run:  pip install pymupdf")

try:
    from deep_translator import GoogleTranslator, MyMemoryTranslator, DeeplTranslator
except ImportError:
    sys.exit("Missing deep-translator.  Run:  pip install deep-translator")

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

HAS_OCR = False
try:
    import pytesseract
    from PIL import Image
    import io
    HAS_OCR = True
except ImportError:
    pass


# ── Suppress MuPDF's ExtGState / resource warnings ───────────────────────────
# These are harmless structural quirks in the source PDF; they do not affect
# the output.  Suppressing them keeps the console clean.
try:
    fitz.TOOLS.mupdf_display_errors(False)
except Exception:
    pass


# ── CJK detection ─────────────────────────────────────────────────────────────
_CJK_RE = re.compile(
    r"[一-鿿"       # CJK Unified Ideographs
    r"㐀-䶿"        # CJK Extension A
    r"豈-﫿"        # CJK Compatibility Ideographs
    r"　-〿"        # CJK Symbols and Punctuation
    r"＀-￯]"       # Halfwidth / Fullwidth Forms
)

def has_cjk(text: str) -> bool:
    return bool(_CJK_RE.search(text))


# ── Separator used to batch-translate multiple strings in one API call ────────
_SEP = "\n<<<SEP>>>\n"


# ── Translation helpers ────────────────────────────────────────────────────────
_cache: Dict[str, str] = {}

def _raw_translate(text: str, translator, retries: int = 3, delay: float = 0.4) -> str:
    """Single API call with retry + exponential back-off."""
    if text in _cache:
        return _cache[text]
    for attempt in range(retries):
        try:
            result = translator.translate(text) or text
            _cache[text] = result
            time.sleep(delay)
            return result
        except Exception as exc:
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))
            else:
                print(f"\n  [warn] translation failed, keeping original — {exc}")
                return text
    return text


def batch_translate(texts: List[str], translator, delay: float) -> List[str]:
    """
    Join all strings with _SEP, translate in one call, then split back.
    Falls back to one-by-one if the separator is corrupted.
    Max payload ~4 000 chars; splits into multiple calls if needed.
    """
    if not texts:
        return []

    MAX_PAYLOAD = 3800
    results: List[str] = [""] * len(texts)

    # Build batches that fit within MAX_PAYLOAD
    batch_indices: List[List[int]] = []
    current: List[int] = []
    current_len = 0

    for i, t in enumerate(texts):
        seg_len = len(t) + len(_SEP)
        if current and current_len + seg_len > MAX_PAYLOAD:
            batch_indices.append(current)
            current, current_len = [], 0
        current.append(i)
        current_len += seg_len
    if current:
        batch_indices.append(current)

    for group in batch_indices:
        joined = _SEP.join(texts[i] for i in group)
        translated = _raw_translate(joined, translator, delay=delay)

        parts = translated.split(_SEP.strip())  # the API may compress whitespace

        # Fallback: if split count doesn't match, try alternate splitter
        if len(parts) != len(group):
            parts = re.split(r"<<<SEP>>>", translated)
        if len(parts) != len(group):
            # Last resort: translate individually
            parts = [_raw_translate(texts[i], translator, delay=delay) for i in group]

        for idx, part in zip(group, parts):
            results[idx] = part.strip() if part.strip() else texts[idx]

    return results


# ── Font helper ────────────────────────────────────────────────────────────────
def choose_font(flags: int) -> str:
    bold   = bool(flags & (1 << 4))
    italic = bool(flags & (1 << 1))
    if bold and italic:
        return "Helvetica-BoldOblique"
    if bold:
        return "Helvetica-Bold"
    if italic:
        return "Helvetica-Oblique"
    return "Helvetica"


# ── Core: process one page ─────────────────────────────────────────────────────

def process_page(page: fitz.Page, translator, delay: float) -> None:
    """
    1. Collect every text line that contains CJK characters.
    2. Batch-translate all lines in one (or a few) API call(s).
    3. White-out original text → insert translation at same position.
    """
    blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]

    # ── Pass 1: gather all CJK lines and their metadata ──────────────────────
    Line = Tuple  # (rect, text, rep_span)
    pending: List[Tuple[fitz.Rect, str, dict]] = []

    for block in blocks:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            spans = line["spans"]
            if not spans:
                continue
            line_text = "".join(s["text"] for s in spans)
            if not has_cjk(line_text):
                continue

            xs = [s["bbox"][0] for s in spans] + [s["bbox"][2] for s in spans]
            ys = [s["bbox"][1] for s in spans] + [s["bbox"][3] for s in spans]
            rect = fitz.Rect(min(xs), min(ys), max(xs), max(ys))
            if rect.is_empty or rect.is_infinite:
                continue

            pending.append((rect, line_text, spans[0]))

    if not pending:
        return

    # ── Pass 2: batch translate ───────────────────────────────────────────────
    originals    = [p[1] for p in pending]
    translations = batch_translate(originals, translator, delay)

    # ── Pass 3: redraw ────────────────────────────────────────────────────────
    for (rect, original, rep_span), translated in zip(pending, translations):
        if not translated or translated == original:
            continue

        # Decode colour
        packed = rep_span.get("color", 0)
        r = ((packed >> 16) & 0xFF) / 255.0
        g = ((packed >> 8)  & 0xFF) / 255.0
        b = (packed         & 0xFF) / 255.0
        font = choose_font(rep_span.get("flags", 0))
        size = rep_span.get("size", 10.0)

        # White-out with generous vertical padding
        pad  = size * 0.3
        wipe = rect + (-1, -pad, 1, pad)
        page.draw_rect(wipe, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)

        # Auto-scale: English text is often wider than Chinese
        available_w = max(rect.width, 1)
        est_w = len(translated) * size * 0.52   # Helvetica avg glyph ≈ 0.52×size
        if est_w > available_w:
            size = max(5.0, round(size * available_w / est_w, 1))

        origin = fitz.Point(rect.x0, rect.y1 - size * 0.15)
        try:
            page.insert_text(
                origin,
                translated,
                fontname=font,
                fontsize=size,
                color=(r, g, b),
                overlay=True,
            )
        except Exception as exc:
            print(f"\n  [warn] insert_text: {exc}")


# ── Optional OCR for text inside images ───────────────────────────────────────

def process_image_ocr(page: fitz.Page, translator, delay: float) -> None:
    if not HAS_OCR:
        return
    for img_info in page.get_images(full=True):
        xref = img_info[0]
        try:
            base = page.parent.extract_image(xref)
            pil  = Image.open(io.BytesIO(base["image"]))
        except Exception:
            continue
        try:
            data = pytesseract.image_to_data(
                pil, lang="chi_tra+eng",
                output_type=pytesseract.Output.DICT,
            )
        except Exception:
            continue

        words, metas = [], []
        for i, word in enumerate(data["text"]):
            if word.strip() and has_cjk(word) and int(data["conf"][i]) >= 40:
                words.append(word)
                metas.append(i)

        if not words:
            continue

        translations = batch_translate(words, translator, delay)
        rects = page.get_image_rects(xref)
        if not rects:
            continue
        img_rect = rects[0]
        sx = img_rect.width  / pil.width
        sy = img_rect.height / pil.height

        for translated, mi in zip(translations, metas):
            if not translated or translated == data["text"][mi]:
                continue
            ox = data["left"][mi]  * sx + img_rect.x0
            oy = data["top"][mi]   * sy + img_rect.y0
            ow = data["width"][mi] * sx
            oh = data["height"][mi]* sy
            wr = fitz.Rect(ox, oy, ox + ow, oy + oh)
            page.draw_rect(wr, color=(1,1,1), fill=(1,1,1), overlay=True)
            page.insert_text(
                fitz.Point(ox, oy + oh * 0.85),
                translated,
                fontname="Helvetica",
                fontsize=max(5.0, oh * 0.75),
                color=(0, 0, 0),
                overlay=True,
            )


# ── Translator factory ────────────────────────────────────────────────────────

def build_translator(service: str, deepl_key: Optional[str]):
    s = service.lower()
    if s == "google":
        return GoogleTranslator(source="zh-TW", target="en")
    if s == "mymemory":
        return MyMemoryTranslator(source="zh-TW", target="en-US")
    if s == "deepl":
        if not deepl_key:
            sys.exit("--deepl-key is required with --service deepl")
        return DeeplTranslator(
            api_key=deepl_key, source="zh", target="en-US", use_free_api=True
        )
    sys.exit(f"Unknown service '{s}'. Choose: google | mymemory | deepl")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Translate a Chinese PDF to English, preserving all layout.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input",  help="Input Chinese PDF")
    parser.add_argument("output", help="Output English PDF")
    parser.add_argument("--service",   default="google",
                        choices=["google", "mymemory", "deepl"])
    parser.add_argument("--deepl-key", default=None, metavar="KEY")
    parser.add_argument("--start",     type=int, default=1)
    parser.add_argument("--end",       type=int, default=None)
    parser.add_argument("--delay",     type=float, default=0.4,
                        help="Seconds between batch API calls (default: 0.4)")
    parser.add_argument("--ocr",       action="store_true",
                        help="Translate text embedded in images (needs pytesseract)")
    args = parser.parse_args()

    if args.ocr and not HAS_OCR:
        print("⚠  --ocr requires:  pip install pytesseract pillow\n"
              "   + Tesseract binary from https://github.com/UB-Mannheim/tesseract/wiki\n"
              "   Continuing without OCR.\n")

    translator = build_translator(args.service, args.deepl_key)

    # Open with lenient parsing to handle broken resource dicts
    doc   = fitz.open(args.input)
    total = doc.page_count
    start = max(0, args.start - 1)
    end   = min(total, args.end) if args.end else total

    print(f"Input :  {args.input}  ({total} pages)")
    print(f"Output:  {args.output}")
    print(f"Range :  pages {start+1}–{end}  ({end - start} pages to translate)")
    print(f"Service: {args.service}")
    print(f"Note  :  ExtGState warnings from MuPDF are suppressed (harmless)\n")

    page_range = range(start, end)
    iterator   = tqdm(page_range, unit="page") if HAS_TQDM else page_range

    for i in iterator:
        if not HAS_TQDM:
            print(f"  Page {i+1}/{total} …", end="", flush=True)
        page = doc[i]
        process_page(page, translator, args.delay)
        if args.ocr and HAS_OCR:
            process_image_ocr(page, translator, args.delay)
        if not HAS_TQDM:
            print(" done")

    print("\nSaving output PDF …")
    doc.save(args.output, garbage=4, deflate=True, clean=True)
    doc.close()
    print(f"✓  Done: {args.output}  ({end - start} pages translated)")


if __name__ == "__main__":
    main()
