#!/usr/bin/env python3
"""Find and list journal files from the output directory.

Replaces inline Python one-liners used in command files for robustness.
"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

from journal_config import load_config


def get_output_dir() -> Path:
    config = load_config()
    output_dir = config.get("output_dir", "~/claude-memoir-journal")
    return Path(output_dir).expanduser()


def list_daily(year_month: str) -> list[str]:
    """List daily journal files for a given YYYY-MM."""
    parts = year_month.split("-")
    if len(parts) != 2:
        return []
    year, month = parts
    daily_dir = get_output_dir() / year / month
    if not daily_dir.exists():
        return []
    return sorted(str(f) for f in daily_dir.glob("*.md"))


def list_dailies_for_week(week_str: str) -> list[str]:
    """List daily journal files that fall within a given ISO week."""
    m = re.match(r"(\d{4})-W(\d{2})", week_str)
    if not m:
        return []
    year, week_num = int(m.group(1)), int(m.group(2))
    jan4 = datetime(year, 1, 4)
    start = jan4 - timedelta(days=jan4.weekday()) + timedelta(weeks=week_num - 1)

    output_dir = get_output_dir()
    files = []
    for i in range(7):
        day = start + timedelta(days=i)
        y, mo = day.strftime("%Y"), day.strftime("%m")
        journal = output_dir / y / mo / f"{day.strftime('%Y-%m-%d')}.md"
        if journal.exists():
            files.append(str(journal))
    return files


def list_weekly(year: str) -> list[str]:
    """List weekly journal files for a given YYYY."""
    year_dir = get_output_dir() / year
    if not year_dir.exists():
        return []
    return sorted(str(f) for f in year_dir.glob(f"{year}-W*.md"))


def list_recent(limit: int = 20) -> list[str]:
    """List most recent journal files across all types."""
    output_dir = get_output_dir()
    if not output_dir.exists():
        return []
    files = sorted(
        output_dir.rglob("*.md"),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
    return [str(f) for f in files[:limit]]


def main() -> None:
    parser = argparse.ArgumentParser(description="Find memoir-journal files")
    parser.add_argument("--daily", metavar="YYYY-MM", help="List daily journals for month")
    parser.add_argument("--for-week", metavar="YYYY-WNN", help="List daily journals for ISO week dates")
    parser.add_argument("--weekly", metavar="YYYY", help="List weekly journals for year")
    parser.add_argument("--recent", type=int, nargs="?", const=20, help="List recent journals (default: 20)")
    args = parser.parse_args()

    if args.daily:
        files = list_daily(args.daily)
    elif args.for_week:
        files = list_dailies_for_week(args.for_week)
    elif args.weekly:
        files = list_weekly(args.weekly)
    elif args.recent is not None:
        files = list_recent(args.recent)
    else:
        files = list_recent(20)

    if files:
        print("\n".join(files))
    else:
        print("No journals found")


if __name__ == "__main__":
    main()
