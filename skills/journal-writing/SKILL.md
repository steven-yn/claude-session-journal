---
name: journal-writing
description: This skill should be used when the user asks to "write a journal", "create a dev log", "summarize today's work", "what did I do today", "일지 작성", "오늘 뭐 했지", "세션 요약", "개발 일지", "회고 작성", or discusses session summary and reflection topics.
version: 1.0.0
---

# Journal Writing Skill

Claude Code 세션 데이터를 기반으로 회고 저널을 작성하는 스킬입니다.

## When This Skill Applies

- 사용자가 오늘/이번 주/이번 달 활동을 돌아보고 싶을 때
- 회고, 저널, 세션 요약을 요청할 때
- "오늘 뭐 했지?", "이번 주 정리해줘" 같은 요청

## How to Use

이 스킬이 활성화되면, 적절한 저널 커맨드를 안내하세요:

- `/journal-daily [YYYY-MM-DD]` — 일별 저널 생성
- `/journal-weekly [YYYY-WNN]` — 주별 저널 생성
- `/journal-monthly [YYYY-MM]` — 월별 저널 생성
- `/journal-status` — 저널 현황 조회
- `/journal-config` — 설정 조회/수정

## Writing Process (4단계 에이전트 파이프라인)

저널 생성 시 아래 4개의 전문 에이전트를 **순차적으로** 실행합니다.
각 에이전트의 출력이 다음 에이전트의 입력이 됩니다.

```
세션 데이터 → [data-analyst] → [journal-writer] → [verifier] → [editor] → 최종 저널
```

| 단계 | 에이전트 | 역할 |
|------|----------|------|
| 1 | **data-analyst** | 세션 데이터를 분석하여 독립 항목으로 분류 |
| 2 | **journal-writer** | 분류된 항목 목록으로 저널 초안 작성 |
| 3 | **verifier** | 완성도(누락 검토)와 사실 정확성을 동시에 검증 |
| 4 | **editor** | 검증된 초안의 가독성과 문체를 최종 편집 |

각 에이전트의 상세 역할과 입출력 형식은 `agents/` 디렉토리의 에이전트 정의를 참조하세요.

## Writing Principles

### 핵심 인사이트 정제
- Raw 세션 로그를 그대로 복사하지 않음
- 의미 있는 배움, 결정, 시행착오만 추출
- "무엇을 했는가"보다 "무엇을 배웠는가"에 집중

### 문체와 톤
- 블로그 포스트로 재활용 가능한 자연스러운 문체
- 적당한 이모지나 장식 사용으로 깔끔하게
- 코드 스니펫은 핵심적인 부분만 포함

### 구조화
- 주제/맥락별로 활동 내용 그룹핑
- 어려움은 **상황 → 시도 → 결과** 구조로 기록
- 통계는 테이블 형태로 깔끔하게

### 다국어 지원
- 설정의 `resolved_language`에 따라 해당 언어로 전체 작성
- 섹션 제목도 해당 언어로 변경
