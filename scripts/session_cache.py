#!/usr/bin/env python3
"""Stop hook: cache session metadata for faster journal generation.

Called by Claude Code on session stop. Reads stdin for hook data,
extracts quick metadata from the current session, and saves to cache.
Always exits 0 and outputs {} to stdout.
"""

import json
import sys
from pathlib import Path

from session_parser import find_session_file, parse_session_file, validate_session_id

CACHE_DIR = Path.home() / ".claude-memoir-journal" / "cache"


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
        session_id = input_data.get("session_id", "")
        cwd = input_data.get("cwd", "")

        if not session_id or not validate_session_id(session_id):
            print(json.dumps({}))
            sys.exit(0)

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
        with open(cache_file, "w") as f:
            json.dump(metadata, f, ensure_ascii=False)

    except Exception as e:
        print(f"claude-memoir-journal cache error: {e}", file=sys.stderr)

    print(json.dumps({}))
    sys.exit(0)


if __name__ == "__main__":
    main()
