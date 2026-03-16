---
description: 월별 저널 생성 - 주별 저널 기반 월간 리뷰
argument-hint: "[YYYY-MM] (기본값: 이번 달)"
allowed-tools: [Read, Write, Bash, Glob, Grep]
---

# Monthly Journal Generator

## Configuration

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal_config.py --get`

## Session Data

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/collect_sessions.py --month ${ARGUMENTS:-$(date +%Y-%m)}`

## Existing Weekly Journals

!`ls $(python3 -c "import json; c=json.load(open('$HOME/.claude-memoir-journal/config.json')) if __import__('os').path.exists('$HOME/.claude-memoir-journal/config.json') else {}; print(c.get('output_dir','~/claude-memoir-journal').replace('~','$HOME'))")/$(date +%Y)/*.md 2>/dev/null || echo "No weekly journals found"`

## Existing Daily Journals

!`ls $(python3 -c "import json; c=json.load(open('$HOME/.claude-memoir-journal/config.json')) if __import__('os').path.exists('$HOME/.claude-memoir-journal/config.json') else {}; print(c.get('output_dir','~/claude-memoir-journal').replace('~','$HOME'))")/$(date +%Y)/$(date +%m)/*.md 2>/dev/null || echo "No daily journals found"`

## Instructions

위 데이터를 기반으로 월간 저널을 생성하세요.

### 저널 저장 경로

설정의 `output_dir` 아래 `YYYY/YYYY-MM.md` 형태로 저장하세요.
예: `~/claude-memoir-journal/2026/2026-03.md`

### 작성 언어

설정의 `resolved_language` 값에 해당하는 언어로 전체 저널을 작성하세요.

### 데이터 활용 우선순위

1. 주별 저널 → 2. 일별 저널 → 3. raw 세션 데이터

### 마크다운 구조

```markdown
---
title: "YYYY-MM 월간 회고"
date: YYYY-MM-DD
month: YYYY-MM
tags: [자동생성태그들]
summary: "한줄 요약"
---

# YYYY-MM 월간 회고

## 이번 달 요약
(한 달을 관통하는 핵심 흐름과 방향)

## 주요 성과
(이번 달 이룬 것들, 의미 있었던 결과물)

## 성장과 변화
(이번 달 새로 배운 것, 달라진 점, 넓어진 시야)

## 회고

### 잘한 점
- ...

### 아쉬운 점
- ...

## 월간 통계
| 항목 | 수치 |
|------|------|
| 총 세션 수 | N |
| 활동 일수 | N |
| 총 토큰 | N |
```
