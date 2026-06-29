import pdfplumber
from deep_translator import GoogleTranslator
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import time
import re
import sys

INPUT_PDF = '/sessions/laughing-tender-fermat/mnt/uploads/Electronic book-All.pdf'
OUTPUT_PDF = '/sessions/laughing-tender-fermat/mnt/outputs/Electronic book-All-English.pdf'

def contains_chinese(text):
    return bool(re.search(r'[一-鿿]', text))

def translate_text(text, translator, max_retries=3):
    """Translate text, handling long texts by chunking."""
    if not text or not text.strip():
        return text
    if not contains_chinese(text):
        return text

    # Split into chunks of max 4500 chars
    MAX_CHUNK = 4500
    chunks = []
    while len(text) > MAX_CHUNK:
        split_at = text[:MAX_CHUNK].rfind('\n')
        if split_at < 0:
            split_at = MAX_CHUNK
        chunks.append(text[:split_at])
        text = text[split_at:]
    chunks.append(text)

    translated_chunks = []
    for chunk in chunks:
        if not chunk.strip():
            translated_chunks.append(chunk)
            continue
        for attempt in range(max_retries):
            try:
                result = translator.translate(chunk)
                translated_chunks.append(result)
                time.sleep(0.3)  # rate limit
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    print(f"  Translation failed: {e}")
                    translated_chunks.append(chunk)

    return ''.join(translated_chunks)

def build_pdf(pages_content, output_path):
    """Build a PDF from translated page content."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'Normal_Custom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=6,
    )
    heading_style = ParagraphStyle(
        'Heading_Custom',
        parent=styles['Heading1'],
        fontSize=13,
        leading=18,
        spaceBefore=12,
        spaceAfter=8,
    )
    page_header_style = ParagraphStyle(
        'PageHeader',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        leading=10,
    )

    story = []

    for page_num, content in enumerate(pages_content, 1):
        if page_num > 1:
            story.append(PageBreak())

        # Page header
        story.append(Paragraph(f"Page {page_num}", page_header_style))
        story.append(Spacer(1, 6))

        if not content or not content.strip():
            continue

        # Split into paragraphs
        paragraphs = content.split('\n')
        for para in paragraphs:
            para = para.strip()
            if not para:
                story.append(Spacer(1, 4))
                continue

            # Detect headings (short lines, possibly starting with numbers)
            is_heading = (
                len(para) < 80 and
                (re.match(r'^[\d\-\.]+[\s一-鿿]', para) or
                 re.match(r'^(Chapter|Section|Part)\s', para, re.IGNORECASE))
            )

            style = heading_style if is_heading else normal_style

            # Escape special chars for reportlab
            para_safe = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            try:
                story.append(Paragraph(para_safe, style))
            except Exception as e:
                print(f"  Para error on page {page_num}: {e}")
                story.append(Paragraph("[content]", style))

    doc.build(story)

def main():
    translator = GoogleTranslator(source='zh-TW', target='en')

    print("Opening PDF...")
    with pdfplumber.open(INPUT_PDF) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages: {total_pages}")

        translated_pages = []

        for i, page in enumerate(pdf.pages):
            print(f"  Processing page {i+1}/{total_pages}...", end='', flush=True)

            text = page.extract_text()
            if text:
                translated = translate_text(text, translator)
                translated_pages.append(translated)
                print(f" done ({len(text)} -> {len(translated)} chars)")
            else:
                translated_pages.append("")
                print(" (no text)")

    print("\nBuilding output PDF...")
    build_pdf(translated_pages, OUTPUT_PDF)
    print(f"Done! Output: {OUTPUT_PDF}")

if __name__ == '__main__':
    main()
