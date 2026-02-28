#!/usr/bin/env python3
"""Split a single Markdown plan into multiple files using explicit file markers.

Put markers into your source file:

<!-- FILE: references/P1_design.md -->
# P1 Design
...

<!-- FILE: references/P2_implementation.md -->
# P2 Implementation
...

Then run:
  python split_plan_with_markers.py <source.md> <out_dir>

This avoids heuristic splitting.
"""
import os, sys, re
MARKER_RE = re.compile(r'^<!--\s*FILE:\s*(.+?)\s*-->\s*$', re.MULTILINE)

def main(src_path: str, out_dir: str):
    with open(src_path, 'r', encoding='utf-8') as f:
        src = f.read()

    matches = list(MARKER_RE.finditer(src))
    if not matches:
        raise SystemExit('No FILE markers found.')

    for i, m in enumerate(matches):
        rel = m.group(1).strip()
        start = m.end()
        end = matches[i+1].start() if i+1 < len(matches) else len(src)
        chunk = src[start:end].strip() + '\n'
        out_path = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(chunk)
        print(f'Wrote {out_path}')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: split_plan_with_markers.py <source.md> <out_dir>', file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
