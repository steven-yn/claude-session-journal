---
description: 일별 저널 생성 - Claude Code 세션 기반 핵심 인사이트
argument-hint: "[YYYY-MM-DD] (기본값: 오늘)"
allowed-tools: [Read, Write, Bash, Glob, Grep]
---

# Daily Journal Generator

## Configuration

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal_config.py --get`

## Session Data

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/collect_sessions.py --date ${ARGUMENTS:-$(date +%Y-%m-%d)}`

## Instructions

위 세션 데이터와 설정을 기반으로 일별 저널을 생성하세요.

### 저널 저장 경로

설정의 `output_dir`를 확인하고, `YYYY/MM/YYYY-MM-DD.md` 형태로 저장하세요.
예: `~/claude-memoir-journal/2026/03/2026-03-14.md`

경로에 `~`가 포함되어 있으면 홈 디렉토리로 확장하세요.

### 작성 언어

설정의 `resolved_language` 값에 해당하는 언어로 전체 저널을 작성하세요.
- `ko` → 한국어, `en` → English, `ja` → 日本語, etc.
- 섹션 제목, 본문, 요약 모두 해당 언어로 작성

### 마크다운 구조

```markdown
---
title: "YYYY-MM-DD 회고"
date: YYYY-MM-DD
tags: [자동생성태그들]
summary: "한줄 요약"
---

# YYYY-MM-DD 회고

## 한줄 요약
(오늘 하루를 한 문장으로)

## 오늘 한 일
(세션 데이터를 바탕으로, 주제/맥락별로 자유롭게 구성)

## 배운 것
(새로 알게 된 것, 깨달은 점 — raw 로그가 아닌 정제된 인사이트)

## 겪은 어려움
(어려웠던 점과 어떻게 풀었는지, 또는 아직 풀지 못한 것)

## 통계
| 항목 | 수치 |
|------|------|
| 세션 수 | N |
| 총 토큰 | N |
```
