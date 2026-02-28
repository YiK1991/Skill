#!/usr/bin/env python3
"""
Initialize a new PDCA coding session with logging template.

Usage:
    python init_session.py "Feature name" --objective "Business objective"
    python init_session.py "JWT Auth" --objective "Add user authentication to API"
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path


def _load_template():
    """Load session template from assets/session-template.md (SSOT).

    Falls back to a minimal inline template if the asset file is not found.
    """
    # Resolve relative to this script's location: ../assets/session-template.md
    asset_path = (
        Path(__file__).resolve().parent.parent / "assets" / "session-template.md"
    )
    if asset_path.exists():
        return asset_path.read_text(encoding="utf-8")
    # Minimal fallback (should not happen in normal installs)
    return (
        "# PDCA Session Log\n\n"
        "**Session Date:** {date}\n"
        "**Feature:** {feature}\n"
        "**Estimated Time:** {estimated_time} hours\n\n"
        "## Business Objective\n\n{objective}\n\n---\n"
    )


def create_session_log(feature, objective, output_dir, estimated_time=2):
    """Create a new session log file."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    # Create safe filename
    safe_feature = "".join(
        c if c.isalnum() or c in ("-", "_") else "_" for c in feature.lower()
    )
    filename = f"session_{date_str}_{safe_feature}.md"

    # Load template from SSOT and fill variables
    template = _load_template()
    content = template.replace("YYYY-MM-DD", date_str)
    content = content.replace("[Feature name]", feature)
    content = content.replace("[X] hours", f"{estimated_time} hours")
    content = content.replace("[What are you trying to achieve and why?]", objective)

    # Write file
    output_path = output_dir / filename
    output_path.write_text(content, encoding="utf-8")

    # Ensure scratch/tool_outputs directory exists for offloaded outputs
    tool_outputs_dir = output_dir / "scratch" / "tool_outputs"
    tool_outputs_dir.mkdir(parents=True, exist_ok=True)

    # Ensure scratch investigation directories exist
    for subdir in ["investigation", "references", "history", "worker_reports"]:
        (output_dir / "scratch" / subdir).mkdir(parents=True, exist_ok=True)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Initialize a new PDCA coding session")
    parser.add_argument("feature", help="Name of the feature being implemented")
    parser.add_argument(
        "--objective", required=True, help="Business objective for this session"
    )
    parser.add_argument(
        "--time", type=float, default=2.0, help="Estimated time in hours (default: 2)"
    )
    parser.add_argument(
        "--output", help="Output directory (default: current directory)"
    )

    args = parser.parse_args()

    output_dir = Path(args.output) if args.output else Path.cwd()
    if not output_dir.exists():
        print(f"Creating output directory: {output_dir}")
        output_dir.mkdir(parents=True)

    try:
        session_file = create_session_log(
            args.feature, args.objective, output_dir, args.time
        )
        print(f"\n✅ Session log created: {session_file}")
        print("\nNext steps:")
        print("1. Review Working Agreements")
        print("2. Load references/analysis-prompt.md")
        print("3. Fill in the session log as you progress")
        print("\nGood luck with your session! 🚀\n")
    except Exception as e:
        print(f"Error creating session log: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
