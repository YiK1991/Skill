#!/usr/bin/env python3
"""Extract a DOCX outline (Heading 1/2/3 text) to help you restructure a long plan."""
import sys
from docx import Document

def is_heading(style_name: str) -> bool:
    return style_name and style_name.startswith("Heading")

def main(path: str):
    doc = Document(path)
    for p in doc.paragraphs:
        style = p.style.name if p.style else ""
        if is_heading(style):
            text = p.text.strip()
            if not text:
                continue
            # Heading N -> indent
            try:
                level = int(style.split()[-1])
            except Exception:
                level = 1
            indent = "  " * max(0, level-1)
            print(f"{indent}- {text}")
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: docx_outline.py <file.docx>', file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1])
