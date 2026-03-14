# claude-memoir-journal

Claude Code 세션 기반으로 일별/주별/월별 마크다운 개발 저널을 자동 생성하는 플러그인입니다.

단순한 세션 로그가 아닌 **핵심 인사이트를 정제**하여, 회고와 기술 블로그에 바로 재활용할 수 있는 저널을 만들어줍니다.

## 주요 기능

- **일별 저널** — 하루 작업의 핵심 인사이트, 학습 내용, 해결한 문제 요약
- **주별 회고** — 일별 저널을 종합한 주간 리뷰, 트렌드와 회고
- **월별 리뷰** — 성장 트렌드, 성과, 방향성을 담은 월간 분석
- **자동 캐싱** — Stop 훅으로 세션 메타데이터를 캐싱하여 빠른 저널 생성
- **다국어 지원** — 시스템 로캘에 맞춰 자동으로 해당 언어로 작성
- **블로그 대응** — YAML frontmatter, 자동 태그, 깔끔한 마크다운 출력

## 설치

```bash
claude plugin add sung-yeon/claude-memoir-journal
```

또는 로컬 플러그인으로 사용:

```bash
git clone https://github.com/sung-yeon/claude-memoir-journal.git ~/projects/claude-memoir-journal
claude --plugin-dir ~/projects/claude-memoir-journal
```

## 요구사항

- Claude Code CLI
- Python 3.10+
- macOS 또는 Linux (Windows는 WSL 사용)

## 사용법

### 커맨드

| 커맨드 | 설명 |
|--------|------|
| `/journal-daily [YYYY-MM-DD]` | 일별 저널 생성 (기본값: 오늘) |
| `/journal-weekly [YYYY-WNN]` | 주별 저널 생성 (기본값: 이번 주) |
| `/journal-monthly [YYYY-MM]` | 월별 저널 생성 (기본값: 이번 달) |
| `/journal-config [show\|set key value]` | 설정 조회/수정 |
| `/journal-status` | 저널 현황, 미작성 날짜, 캐시 정보 |

### 사용 예시

```
/journal-daily
/journal-daily 2026-03-14
/journal-weekly 2026-W11
/journal-monthly 2026-03
/journal-config set language ko
/journal-config set output_dir ~/my-dev-journal
```

## 설정

설정 파일: `~/.claude-memoir-journal/config.json`

| 키 | 타입 | 기본값 | 설명 |
|----|------|--------|------|
| `output_dir` | string | `~/claude-memoir-journal` | 저널 저장 경로 |
| `language` | string | `auto` | 작성 언어 (auto/ko/en/ja 등) |
| `include_token_stats` | bool | `true` | 토큰 통계 포함 |
| `include_code_snippets` | bool | `true` | 코드 스니펫 포함 |
| `max_code_snippet_lines` | int | `10` | 스니펫 최대 줄 수 |
| `blog_frontmatter` | bool | `true` | YAML frontmatter 포함 |
| `tags_auto_generate` | bool | `true` | 태그 자동 생성 |
| `exclude_projects` | list | `[]` | 제외할 프로젝트 경로 |

## 출력 구조

`output_dir` 아래에 저널이 저장됩니다:

```
~/claude-memoir-journal/
├── 2026/
│   ├── 03/
│   │   ├── 2026-03-14.md    # 일별
│   │   └── 2026-03-15.md
│   ├── 2026-W11.md           # 주별
│   └── 2026-03.md            # 월별
```

## 동작 원리

1. **세션 수집** — `~/.claude/history.jsonl`과 세션 JSONL 파일을 파싱
2. **데이터 추출** — 사용자 질문, 도구 사용, 수정 파일, 토큰 통계 추출
3. **인사이트 정제** — Claude가 raw 데이터를 분석하여 구조화된 저널 생성
4. **캐싱** — Stop 훅이 세션 메타데이터를 캐싱하여 즉시 활용

## 라이선스

MIT
