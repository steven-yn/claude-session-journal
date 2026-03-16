#!/usr/bin/env python3
"""Configuration manager for claude-memoir-journal plugin."""

import json
import locale
import os
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".claude-memoir-journal"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "output_dir": "~/claude-memoir-journal",
    "language": "auto",
    "include_token_stats": True,
    "include_code_snippets": True,
    "max_code_snippet_lines": 10,
    "blog_frontmatter": True,
    "tags_auto_generate": True,
    "exclude_projects": [],
    "background_summary": True,
    "summary_model": "haiku",
    "summary_timeout": 120,
    "summary_min_queries": 3,
}


def resolve_language(lang_setting: str) -> str:
    if lang_setting != "auto":
        return lang_setting
    try:
        loc = locale.getlocale()[0]
        if loc:
            return loc.split("_")[0]
    except (ValueError, AttributeError):
        pass
    lang = os.environ.get("LANG", "")
    if lang:
        code = lang.split("_")[0].split(".")[0]
        if code:
            return code
    return "en"


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                user_config = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: could not load config, using defaults: {e}", file=sys.stderr)
            user_config = {}
        config = {**DEFAULT_CONFIG, **user_config}
    else:
        config = DEFAULT_CONFIG.copy()
    config["resolved_language"] = resolve_language(config["language"])
    return config


def save_config(config: dict) -> None:
    save = {k: v for k, v in config.items() if k != "resolved_language"}
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(save, f, indent=2, ensure_ascii=False)


def init_config() -> dict:
    if CONFIG_FILE.exists():
        return load_config()
    config = DEFAULT_CONFIG.copy()
    save_config(config)
    return load_config()


def set_value(key: str, value: str) -> dict:
    config = load_config()
    if key not in DEFAULT_CONFIG:
        print(f"Unknown config key: {key}", file=sys.stderr)
        sys.exit(1)

    expected_type = type(DEFAULT_CONFIG[key])
    if expected_type is bool:
        value = value.lower() in ("true", "1", "yes")
    elif expected_type is int:
        value = int(value)
    elif expected_type is list:
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            print(f"Invalid JSON for list value: {value}", file=sys.stderr)
            sys.exit(1)

    config[key] = value
    save_config(config)
    return load_config()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="claude-memoir-journal config manager")
    parser.add_argument("--get", action="store_true", help="Show current config")
    parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set config value")
    parser.add_argument("--init", action="store_true", help="Initialize default config")
    args = parser.parse_args()

    if args.init:
        config = init_config()
        print(json.dumps(config, indent=2, ensure_ascii=False))
    elif args.set:
        config = set_value(args.set[0], args.set[1])
        print(json.dumps(config, indent=2, ensure_ascii=False))
    else:
        config = load_config()
        print(json.dumps(config, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
