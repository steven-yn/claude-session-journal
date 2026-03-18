---
description: 일별 저널 생성 - Claude Code 세션 기반 핵심 인사이트
argument-hint: "[YYYY-MM-DD] (기본값: 오늘)"
allowed-tools: [Read, Write, Bash, Glob, Grep]
---

# Daily Journal Generator

## Configuration

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal_config.py --get`

## Session Data

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/collect_sessions.py --date ${ARGUMENTS:-$(date +%Y-%m-%d)} --check-summary`

## Instructions

**세션 데이터가 없는 경우**: 위 세션 데이터의 `total_sessions`가 0이면, 해당 날짜에 Claude Code 세션이 없다고 사용자에게 알리고 파이프라인을 실행하지 마세요.

위 세션 데이터와 설정을 기반으로 아래 에이전트 파이프라인을 실행하여 일별 저널을 생성하세요.

### Level 2 캐시 분기 로직

세션 데이터의 `summary_stats`와 각 세션의 `has_summary` 필드를 확인하여 아래 3가지 케이스를 판별하세요:

**Case A — 모든 세션이 `has_summary: true`**:
- data-analyst 단계를 **스킵**합니다.
- 각 세션의 `summary_data.summary`를 아래 형식으로 `$TMPDIR/memoir-journal-pipeline/1-analysis.md`에 직접 변환하여 저장:
  - `summary.topics` → 각 topic을 `### 항목 N: {title}` 형식으로 변환
  - `topic.category` → `유형`, `topic.description` → `요약`
  - `topic.key_decisions` → `핵심 결정`, `topic.insights` → `인사이트`, `topic.difficulties` → `어려움`
  - `topic.files_involved` → `관련 파일`
  - `summary.overall_learnings` → `## 전체 배움` 섹션
  - `summary.one_line` → 파일 상단에 한줄 요약 포함
- 이후 journal-writer → verifier → editor 순서로 진행

**Case B — 일부만 `has_summary: true`**:
- `has_summary: true`인 세션의 `summary_data`를 위 Case A 방식으로 수집
- `has_summary: false`인 세션만 data-analyst 에이전트에 전달하여 분석 (병렬 실행 가능)
- 두 결과를 병합하여 `1-analysis.md`에 저장
- 이후 journal-writer → verifier → editor 순서로 진행

**Case C — 모든 세션이 `has_summary: false`**:
- 기존과 동일한 전체 파이프라인 실행

### 에이전트 파이프라인 (서브에이전트 격리 실행)

각 단계를 **Agent 도구를 사용하여 서브에이전트로** 실행하세요. 서브에이전트는 독립된 컨텍스트에서 작업하므로 메인 컨텍스트가 보호됩니다.

**임시 작업 디렉토리**: 파이프라인 시작 전 `$TMPDIR/memoir-journal-pipeline/` 디렉토리를 생성하세요. 각 단계의 출력을 이 디렉토리에 파일로 저장하고, 다음 단계의 서브에이전트가 해당 파일을 읽도록 합니다.

1. **data-analyst** — Agent 도구로 실행. 프롬프트에 위 세션 데이터 전체를 포함하여 독립 항목으로 분류하도록 지시. 결과를 `$TMPDIR/memoir-journal-pipeline/1-analysis.md`에 저장. **Case A에서는 스킵, Case B에서는 미스 세션만 전달**
2. **journal-writer** — Agent 도구로 실행. `1-analysis.md`를 읽고 + 아래 마크다운 구조/설정을 포함하여 저널 초안 작성. 결과를 `$TMPDIR/memoir-journal-pipeline/2-draft.md`에 저장
3. **verifier** — Agent 도구로 실행. `2-draft.md`를 읽고 + 원본 세션 데이터와 대조하여 완성도(누락 검토)와 사실 정확성을 검증. 문제가 있으면 수정한 최종본을, 없으면 원본 그대로 `$TMPDIR/memoir-journal-pipeline/3-verified.md`에 저장
4. **editor** — Agent 도구로 실행. `3-verified.md`를 읽고 + 작성 언어 설정을 포함하여 최종 편집. 결과를 `$TMPDIR/memoir-journal-pipeline/4-final.md`에 저장

각 Agent 호출 시 프롬프트에 포함할 내용:
- 해당 에이전트의 역할 설명 (agents/ 디렉토리 참조)
- 읽어야 할 입력 파일 경로
- 출력을 저장할 파일 경로
- 원본 세션 데이터가 필요한 단계(3)는 세션 데이터도 프롬프트에 포함

파이프라인 완료 후, `4-final.md`의 내용을 저널 파일로 저장하세요.

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

## 겪은 어려움
(어려웠던 점과 어떻게 풀었는지, 또는 아직 풀지 못한 것)

## 배운 것
(새로 알게 된 것, 깨달은 점 — raw 로그가 아닌 정제된 인사이트)

## 작업 통계
> 아래는 오늘 Claude Code 세션에서 소비한 토큰이며, 이 저널 생성 비용이 아닙니다.

| 항목 | 수치 |
|------|------|
| 세션 수 | N |
| 새로 처리한 토큰 (input_new) | N |
| 컨텍스트 캐시 (input_cache_read) | N |
| 출력 토큰 | N |
```
