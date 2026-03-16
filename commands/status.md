---
description: 저널 현황 조회 - 최근 저널, 미작성 날짜, 캐시 현황
allowed-tools: [Bash, Read, Glob]
---

# Journal Status

## Configuration

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal_config.py --get`

## Recent Journals

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/find_journals.py --recent 20`

## Cache Status

!`ls ~/.claude-memoir-journal/cache/*.json 2>/dev/null | wc -l | tr -d ' '`

## Summary Cache Status

!`ls ~/.claude-memoir-journal/cache/*.summary.json 2>/dev/null | wc -l | tr -d ' '`

## Recent Sessions (Last 7 days)

!`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/collect_sessions.py --week $(date +%Y-W%V) 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Sessions: {d[\"total_sessions\"]}'); print(f'Tokens: {d[\"total_tokens\"]}')" 2>/dev/null || echo "No session data available"`

## Instructions

위 정보를 기반으로 저널 현황을 보기 좋게 요약하세요:

1. **최근 저널 목록**: 파일명과 날짜. "No journals found"이면 아직 생성된 저널이 없다고 안내
2. **미작성 날짜**: 세션은 있지만 저널이 없는 날짜 식별
3. **캐시 현황**: 캐시된 세션 수
4. **Level 2 요약 캐시 수**: 백그라운드 요약이 완료된 세션 수
5. **이번 주 통계**: 세션 수, 토큰 사용량. "No session data available"이면 이번 주 세션이 없다고 안내

미작성 날짜가 있으면 `/journal-daily YYYY-MM-DD`로 생성할 수 있다고 안내하세요.
아직 저널을 한 번도 생성하지 않은 사용자에게는 `/journal-daily`로 첫 저널을 만들어보라고 안내하세요.
