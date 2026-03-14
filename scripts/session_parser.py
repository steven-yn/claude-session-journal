#!/usr/bin/env python3
"""Shared utilities for parsing Claude Code session data."""

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CLAUDE_DIR = Path.home() / ".claude"
PROJECTS_DIR = CLAUDE_DIR / "projects"

SESSION_ID_PATTERN = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")


def validate_session_id(session_id: str) -> bool:
    return bool(SESSION_ID_PATTERN.fullmatch(session_id))


def encode_project_path(path: str) -> str:
    return path.replace("/", "-").lstrip("-")


def parse_timestamp(ts: Any) -> datetime | None:
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def find_session_file(session_id: str, project_path: str) -> Path | None:
    if not validate_session_id(session_id):
        return None

    encoded = encode_project_path(project_path)
    session_file = PROJECTS_DIR / encoded / f"{session_id}.jsonl"
    if session_file.exists():
        return session_file

    for proj_dir in PROJECTS_DIR.iterdir():
        if not proj_dir.is_dir():
            continue
        candidate = proj_dir / f"{session_id}.jsonl"
        if candidate.exists():
            return candidate
    return None


def parse_session_file(session_file: Path) -> dict:
    """Parse a session JSONL file, streaming line by line."""
    user_queries: list[str] = []
    tools_used: dict[str, int] = defaultdict(int)
    files_modified: set[str] = set()
    total_input = 0
    total_output = 0
    start_time: datetime | None = None
    end_time: datetime | None = None
    git_branch: str | None = None
    conversation_summary: list[str] = []

    with open(session_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts = parse_timestamp(entry.get("timestamp"))
            if ts:
                if start_time is None or ts < start_time:
                    start_time = ts
                if end_time is None or ts > end_time:
                    end_time = ts

            if not git_branch and entry.get("gitBranch"):
                branch = entry["gitBranch"]
                if branch != "HEAD":
                    git_branch = branch

            entry_type = entry.get("type")

            if entry_type == "user":
                content = entry.get("message", {}).get("content", "")
                if isinstance(content, str) and content.strip():
                    text = content.strip()
                    if len(text) > 200:
                        text = text[:200] + "..."
                    user_queries.append(text)

            elif entry_type == "assistant":
                msg = entry.get("message", {})
                usage = msg.get("usage", {})
                total_input += usage.get("input_tokens", 0)
                total_input += usage.get("cache_read_input_tokens", 0)
                total_input += usage.get("cache_creation_input_tokens", 0)
                total_output += usage.get("output_tokens", 0)

                for block in msg.get("content", []):
                    if not isinstance(block, dict):
                        continue

                    if block.get("type") == "tool_use":
                        tool_name = block.get("name", "unknown")
                        tools_used[tool_name] += 1
                        tool_input = block.get("input", {})
                        fp = tool_input.get("file_path") or tool_input.get("path") or ""
                        if fp and tool_name in ("Edit", "Write", "NotebookEdit"):
                            files_modified.add(fp)

                    elif block.get("type") == "text":
                        text = block.get("text", "")
                        if text and len(text) > 20:
                            summary = text[:300] + "..." if len(text) > 300 else text
                            conversation_summary.append(summary)

    return {
        "user_queries": user_queries[:20],
        "tools_used": dict(tools_used),
        "files_modified": sorted(files_modified),
        "token_usage": {"input": total_input, "output": total_output},
        "start_time": start_time.isoformat() if start_time else None,
        "end_time": end_time.isoformat() if end_time else None,
        "git_branch": git_branch or "unknown",
        "conversation_summary": conversation_summary[:10],
    }
