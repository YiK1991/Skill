#!/usr/bin/env python3
"""DEPRECATED: use `dispatch_prompt_pack.py` or call `jules_bridge.py` directly.

This script is kept only for compatibility with earlier drafts.
"""

from __future__ import annotations

import sys


def main() -> None:
    print(
        "This script is deprecated. Use:\n"
        "  python scripts/dispatch_prompt_pack.py --pack-dir <...>/jules_pack --repo . --json\n"
        "or call:\n"
        "  python scripts/jules_bridge.py submit --title ... --prompt-file ... --json\n",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
