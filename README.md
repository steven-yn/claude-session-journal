# claude-memoir-journal

A Claude Code plugin that automatically generates daily/weekly/monthly development journals from your Claude Code sessions.

Instead of raw session logs, claude-memoir-journal extracts **key insights** — learnings, decisions, problem-solving processes — and produces markdown journals ready for retrospectives or blog posts.

## Features

- **Daily journals** — Summarize your day's work with key insights, learnings, and solved problems
- **Weekly retrospectives** — Aggregate daily journals into weekly reviews with trends and reflections
- **Monthly reviews** — Big-picture analysis of growth, achievements, and direction
- **Auto-caching** — Stop hook caches session metadata for faster journal generation
- **Multi-language** — Journals are written in your system locale (or configured language)
- **Blog-ready** — YAML frontmatter, auto-generated tags, clean markdown output

## Installation

```bash
claude plugin add sung-yeon/claude-memoir-journal
```

Or manually clone and use as a local plugin:

```bash
git clone https://github.com/sung-yeon/claude-memoir-journal.git ~/projects/claude-memoir-journal
claude --plugin-dir ~/projects/claude-memoir-journal
```

## Requirements

- Claude Code CLI
- Python 3.10+
- macOS or Linux (Windows via WSL)

## Usage

### Commands

| Command | Description |
|---------|-------------|
| `/journal-daily [YYYY-MM-DD]` | Generate a daily journal (default: today) |
| `/journal-weekly [YYYY-WNN]` | Generate a weekly journal (default: this week) |
| `/journal-monthly [YYYY-MM]` | Generate a monthly journal (default: this month) |
| `/journal-config [show\|set key value]` | View or modify settings |
| `/journal-status` | Show journal status, missing dates, cache info |

### Examples

```
/journal-daily
/journal-daily 2026-03-14
/journal-weekly 2026-W11
/journal-monthly 2026-03
/journal-config set language ko
/journal-config set output_dir ~/my-dev-journal
```

## Configuration

Settings are stored in `~/.claude-memoir-journal/config.json`.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `output_dir` | string | `~/claude-memoir-journal` | Journal output directory |
| `language` | string | `auto` | Writing language (`auto`/`ko`/`en`/`ja`/etc.) |
| `include_token_stats` | bool | `true` | Include token usage statistics |
| `include_code_snippets` | bool | `true` | Include code snippets |
| `max_code_snippet_lines` | int | `10` | Max lines per code snippet |
| `blog_frontmatter` | bool | `true` | Include YAML frontmatter |
| `tags_auto_generate` | bool | `true` | Auto-generate tags |
| `exclude_projects` | list | `[]` | Project paths to exclude |

## Output Structure

Journals are saved under your `output_dir`:

```
~/claude-memoir-journal/
├── 2026/
│   ├── 03/
│   │   ├── 2026-03-14.md    # Daily
│   │   └── 2026-03-15.md
│   ├── 2026-W11.md           # Weekly
│   └── 2026-03.md            # Monthly
```

## How It Works

1. **Session collection** — Parses `~/.claude/history.jsonl` and session JSONL files
2. **Data extraction** — Extracts user queries, tool usage, files modified, token stats
3. **Insight refinement** — Claude analyzes raw data and produces structured, insightful journals
4. **Caching** — Stop hook caches session metadata for instant access

## License

MIT
