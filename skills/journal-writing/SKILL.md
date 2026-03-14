---
name: journal-writing
description: This skill should be used when the user asks to "write a journal", "create a dev log", "summarize today's work", "what did I do today", "일지 작성", "오늘 뭐 했지", "세션 요약", "개발 일지", "회고 작성", or discusses session summary and reflection topics.
version: 1.0.0
---

# Journal Writing Skill

Claude Code 세션 데이터를 기반으로 개발 저널을 작성하는 스킬입니다.

## When This Skill Applies

- 사용자가 오늘/이번 주/이번 달 작업 내용을 정리하고 싶을 때
- 개발 일지, 회고, 세션 요약을 요청할 때
- "오늘 뭐 했지?", "이번 주 정리해줘" 같은 요청

## How to Use

이 스킬이 활성화되면, 적절한 저널 커맨드를 안내하세요:

- `/journal-daily [YYYY-MM-DD]` — 일별 저널 생성
- `/journal-weekly [YYYY-WNN]` — 주별 저널 생성
- `/journal-monthly [YYYY-MM]` — 월별 저널 생성
- `/journal-status` — 저널 현황 조회
- `/journal-config` — 설정 조회/수정

## Writing Principles

저널 작성 시 다음 원칙을 따르세요:

### 핵심 인사이트 정제
- Raw 세션 로그를 그대로 복사하지 않음
- 의미 있는 학습, 결정, 해결 과정만 추출
- "무엇을 했는가"보다 "무엇을 배웠는가"에 집중

### 문체와 톤
- 기술 블로그 포스트로 재활용 가능한 자연스러운 문체
- 과도한 이모지나 장식 없이 깔끔하게
- 코드 스니펫은 핵심적인 부분만 포함

### 구조화
- 프로젝트별로 작업 내용 그룹핑
- 문제 → 접근 → 해결 구조로 트러블슈팅 기록
- 통계는 테이블 형태로 깔끔하게

### 다국어 지원
- 설정의 `resolved_language`에 따라 해당 언어로 전체 작성
- 섹션 제목도 해당 언어로 변경
