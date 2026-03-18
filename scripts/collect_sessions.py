#!/usr/bin/env python3
"""Collect and parse Claude Code session data for journal generation.

Reads history.jsonl and session JSONL files to extract structured session
metadata for a given date range.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from session_parser import (
    CLAUDE_DIR,
    find_session_file,
    parse_session_file,
    parse_timestamp,
    validate_session_id,
)

HISTORY_FILE = CLAUDE_DIR / "history.jsonl"
CACHE_DIR = Path.home() / ".claude-memoir-journal" / "cache"


def get_local_tz() -> timezone:
    offset = datetime.now().astimezone().utcoffset()
    return timezone(offset) if offset else timezone.utc


def date_range_for_day(date_str: str) -> tuple[datetime, datetime]:
    local_tz = get_local_tz()
    day = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=local_tz)
    return day, day + timedelta(days=1)


def date_range_for_week(week_str: str) -> tuple[datetime, datetime]:
    local_tz = get_local_tz()
    m = re.match(r"(\d{4})-W(\d{2})", week_str)
    if not m:
        raise ValueError(f"Invalid week format: {week_str} (expected YYYY-WNN)")
    year, week_num = map(int, m.groups())
    jan4 = datetime(year, 1, 4, tzinfo=local_tz)
    start_of_week1 = jan4 - timedelta(days=jan4.weekday())
    start = start_of_week1 + timedelta(weeks=week_num - 1)
    return start, start + timedelta(weeks=1)


def date_range_for_month(month_str: str) -> tuple[datetime, datetime]:
    local_tz = get_local_tz()
    m = re.match(r"(\d{4})-(\d{2})", month_str)
    if not m:
        raise ValueError(f"Invalid month format: {month_str} (expected YYYY-MM)")
    year, month = map(int, m.groups())
    start = datetime(year, month, 1, tzinfo=local_tz)
    if month == 12:
        end = datetime(year + 1, 1, 1, tzinfo=local_tz)
    else:
        end = datetime(year, month + 1, 1, tzinfo=local_tz)
    return start, end


def filter_history(start: datetime, end: datetime, exclude_projects: list[str]) -> dict[str, dict]:
    """Filter history.jsonl entries by date range, grouped by sessionId."""
    sessions: dict[str, dict] = {}
    if not HISTORY_FILE.exists():
        return sessions

    with open(HISTORY_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts = parse_timestamp(entry.get("timestamp"))
            if not ts or ts < start or ts >= end:
                continue

            project = entry.get("project", "")
            if any(project.startswith(ep) for ep in exclude_projects):
                continue

            sid = entry.get("sessionId", "")
            if not sid or not validate_session_id(sid):
                continue

            if sid not in sessions:
                sessions[sid] = {
                    "session_id": sid,
                    "project": project,
                    "project_name": Path(project).name if project else "unknown",
                    "first_seen": ts,
                    "last_seen": ts,
                    "displays": [],
                }

            sessions[sid]["last_seen"] = max(sessions[sid]["last_seen"], ts)
            display = entry.get("display", "")
            if display and not display.startswith("/"):
                sessions[sid]["displays"].append(display)

    return sessions


def try_load_cache(session_id: str) -> dict | None:
    if not validate_session_id(session_id):
        return None
    cache_file = CACHE_DIR / f"{session_id}.json"
    if cache_file.exists():
        try:
            with open(cache_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return None


def try_load_summary(session_id: str) -> dict | None:
    if not validate_session_id(session_id):
        return None
    summary_file = CACHE_DIR / f"{session_id}.summary.json"
    if summary_file.exists():
        try:
            with open(summary_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return None


def collect(start: datetime, end: datetime, exclude_projects: list[str],
            check_summary: bool = False) -> dict:
    history_sessions = filter_history(start, end, exclude_projects)
    sessions = []
    total_input = 0
    total_output = 0
    total_input_new = 0
    total_input_cache_read = 0
    total_input_cache_write = 0
    summary_hit = 0
    summary_miss = 0

    for sid, meta in history_sessions.items():
        cached = try_load_cache(sid)
        if cached:
            cached["displays"] = meta.get("displays", [])
            if check_summary:
                summary = try_load_summary(sid)
                cached["has_summary"] = summary is not None
                if summary:
                    cached["summary_data"] = summary
                    summary_hit += 1
                else:
                    summary_miss += 1
            sessions.append(cached)
            tu = cached.get("token_usage", {})
            total_input += tu.get("input", 0)
            total_output += tu.get("output", 0)
            total_input_new += tu.get("input_new", 0)
            total_input_cache_read += tu.get("input_cache_read", 0)
            total_input_cache_write += tu.get("input_cache_write", 0)
            continue

        session_file = find_session_file(sid, meta["project"])
        if not session_file:
            continue

        parsed = parse_session_file(session_file)
        session_data = {
            "session_id": sid,
            "project": meta["project"],
            "project_name": meta["project_name"],
            "git_branch": parsed["git_branch"],
            "start_time": parsed["start_time"],
            "end_time": parsed["end_time"],
            "user_queries": parsed["user_queries"],
            "tools_used": parsed["tools_used"],
            "files_modified": parsed["files_modified"],
            "token_usage": parsed["token_usage"],
            "conversation_summary": parsed["conversation_summary"],
            "displays": meta.get("displays", []),
        }
        if check_summary:
            summary = try_load_summary(sid)
            session_data["has_summary"] = summary is not None
            if summary:
                session_data["summary_data"] = summary
                summary_hit += 1
            else:
                summary_miss += 1
        sessions.append(session_data)
        tu = parsed["token_usage"]
        total_input += tu["input"]
        total_output += tu["output"]
        total_input_new += tu.get("input_new", 0)
        total_input_cache_read += tu.get("input_cache_read", 0)
        total_input_cache_write += tu.get("input_cache_write", 0)

    sessions.sort(key=lambda s: s.get("start_time") or "")

    period = start.strftime("%Y-%m-%d")
    if (end - start).days > 1:
        period = f"{start.strftime('%Y-%m-%d')} ~ {(end - timedelta(days=1)).strftime('%Y-%m-%d')}"

    result = {
        "period": period,
        "sessions": sessions,
        "total_tokens": {
            "input": total_input,
            "output": total_output,
            "input_new": total_input_new,
            "input_cache_read": total_input_cache_read,
            "input_cache_write": total_input_cache_write,
        },
        "total_sessions": len(sessions),
    }
    if check_summary:
        result["summary_stats"] = {"hit": summary_hit, "miss": summary_miss}
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect Claude Code session data")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--date", help="Date (YYYY-MM-DD)")
    group.add_argument("--week", help="Week (YYYY-WNN)")
    group.add_argument("--month", help="Month (YYYY-MM)")
    parser.add_argument("--format", default="json", choices=["json"])
    parser.add_argument("--exclude", nargs="*", default=[], help="Project paths to exclude")
    parser.add_argument("--check-summary", action="store_true", help="Check Level 2 summary cache")
    args = parser.parse_args()

    if args.date:
        start, end = date_range_for_day(args.date)
    elif args.week:
        start, end = date_range_for_week(args.week)
    elif args.month:
        start, end = date_range_for_month(args.month)
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        start, end = date_range_for_day(today)

    result = collect(start, end, args.exclude, check_summary=args.check_summary)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
