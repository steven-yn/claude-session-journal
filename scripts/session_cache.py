#!/usr/bin/env python3
"""Stop/SessionEnd hook: cache session metadata for faster journal generation.

Called by Claude Code on session stop and on /clear (SessionEnd with reason=clear).
Reads stdin for hook data, extracts metadata, and saves to cache.
Merges with existing cache to preserve data across /clear boundaries.
Always exits 0 and outputs {} to stdout.
"""

import json
import sys
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
    }

    result = dict(new)
    result["user_queries"] = merged_queries
    result["tools_used"] = merged_tools
    result["files_modified"] = merged_files
    result["token_usage"] = merged_tokens
    return result


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

    except Exception as e:
        print(f"claude-memoir-journal cache error: {e}", file=sys.stderr)

    print(json.dumps({}))
    sys.exit(0)


if __name__ == "__main__":
    main()
