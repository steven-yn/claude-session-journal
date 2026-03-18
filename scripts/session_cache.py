#!/usr/bin/env python3
"""Stop/SessionEnd hook: cache session metadata for faster journal generation.

Called by Claude Code on session stop and on /clear (SessionEnd with reason=clear).
Reads stdin for hook data, extracts metadata, and saves to cache.
Merges with existing cache to preserve data across /clear boundaries.
Always exits 0 and outputs {} to stdout.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from session_parser import find_session_file, parse_session_file, validate_session_id

CACHE_DIR = Path.home() / ".claude-memoir-journal" / "cache"


def merge_cache(existing: dict, new: dict) -> dict:
    """Merge existing cache with new data to preserve info lost by /clear."""
    # Combine user_queries (deduplicated, preserving order)
    seen = set()
    merged_queries = []
    for q in existing.get("user_queries", []) + new.get("user_queries", []):
        if q not in seen:
            seen.add(q)
            merged_queries.append(q)

    # Merge tools_used counts (take the max per tool)
    merged_tools = dict(existing.get("tools_used", {}))
    for tool, count in new.get("tools_used", {}).items():
        merged_tools[tool] = max(merged_tools.get(tool, 0), count)

    # Union files_modified
    merged_files = sorted(
        set(existing.get("files_modified", []))
        | set(new.get("files_modified", []))
    )

    # Sum token_usage
    ex_tokens = existing.get("token_usage", {})
    new_tokens = new.get("token_usage", {})
    merged_tokens = {
        "input": ex_tokens.get("input", 0) + new_tokens.get("input", 0),
        "output": ex_tokens.get("output", 0) + new_tokens.get("output", 0),
        "input_new": ex_tokens.get("input_new", 0) + new_tokens.get("input_new", 0),
        "input_cache_read": ex_tokens.get("input_cache_read", 0) + new_tokens.get("input_cache_read", 0),
        "input_cache_write": ex_tokens.get("input_cache_write", 0) + new_tokens.get("input_cache_write", 0),
    }

    result = dict(new)
    result["user_queries"] = merged_queries
    result["tools_used"] = merged_tools
    result["files_modified"] = merged_files
    result["token_usage"] = merged_tokens
    return result


def check_journal_reminder() -> None:
    """Print reminder if today's journal hasn't been written. Shows once per day."""
    try:
        from journal_config import load_config

        today = datetime.now().strftime("%Y-%m-%d")
        reminder_marker = CACHE_DIR / ".last_reminder"

        if reminder_marker.exists():
            if reminder_marker.read_text().strip() == today:
                return

        config = load_config()
        output_dir = Path(config.get("output_dir", "~/claude-memoir-journal")).expanduser()
        year, month, _ = today.split("-")
        journal_file = output_dir / year / month / f"{today}.md"

        if journal_file.exists():
            return

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        reminder_marker.write_text(today)
        print(
            "\n\U0001f4dd Today's journal hasn't been written yet. "
            "Run /journal-daily to generate one.",
            file=sys.stderr,
        )
    except Exception:
        pass


def spawn_background_summary(session_id: str, parsed: dict, metadata: dict) -> None:
    try:
        from journal_config import load_config

        config = load_config()
        if not config.get("background_summary", True):
            return

        conv_blocks = parsed.get("conversation_blocks", [])
        min_queries = config.get("summary_min_queries", 3)
        if len(metadata.get("user_queries", [])) < min_queries:
            return

        tmp_file = CACHE_DIR / f"{session_id}.conv.tmp.json"
        conv_data = {
            "session_id": session_id,
            "project": metadata.get("project", ""),
            "project_name": metadata.get("project_name", ""),
            "user_queries": metadata.get("user_queries", []),
            "files_modified": metadata.get("files_modified", []),
            "tools_used": metadata.get("tools_used", {}),
            "git_branch": metadata.get("git_branch", "unknown"),
            "conversation_blocks": conv_blocks,
        }
        with open(tmp_file, "w") as f:
            json.dump(conv_data, f, ensure_ascii=False)

        summary_file = CACHE_DIR / f"{session_id}.summary.json"
        summary_file.unlink(missing_ok=True)

        plugin_root = Path(__file__).resolve().parent.parent
        subprocess.Popen(
            [sys.executable, str(plugin_root / "scripts" / "session_summarize.py"),
             session_id, str(tmp_file), str(plugin_root)],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "")
        cwd = input_data.get("cwd", "")

        if not session_id or not validate_session_id(session_id):
            print(json.dumps({}))
            sys.exit(0)

        # SessionEnd provides transcript_path directly; Stop hook needs lookup
        transcript_path = input_data.get("transcript_path", "")
        if transcript_path and Path(transcript_path).exists():
            session_file = Path(transcript_path)
        else:
            session_file = find_session_file(session_id, cwd)
        if not session_file:
            print(json.dumps({}))
            sys.exit(0)

        parsed = parse_session_file(session_file)
        metadata = {
            "session_id": session_id,
            "project": cwd,
            "project_name": Path(cwd).name if cwd else "unknown",
            "user_queries": parsed["user_queries"],
            "tools_used": parsed["tools_used"],
            "files_modified": parsed["files_modified"],
            "token_usage": parsed["token_usage"],
            "git_branch": parsed["git_branch"],
        }

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = CACHE_DIR / f"{session_id}.json"

        # Merge with existing cache to preserve data lost by /clear
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    existing = json.load(f)
                metadata = merge_cache(existing, metadata)
            except (json.JSONDecodeError, OSError):
                pass

        with open(cache_file, "w") as f:
            json.dump(metadata, f, ensure_ascii=False)

        spawn_background_summary(session_id, parsed, metadata)

    except Exception as e:
        print(f"claude-memoir-journal cache error: {e}", file=sys.stderr)

    check_journal_reminder()
    print(json.dumps({}))
    sys.exit(0)


if __name__ == "__main__":
    main()
