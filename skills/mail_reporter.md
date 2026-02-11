# OpenCode 스킬 3개 (메일 헬스체크 → 보고서 → Obsidian 저장)

아래 3개를 그대로 파일로 만들어서 프로젝트에 넣으면 됩니다.

권장 폴더 구조:

```
.opencode/
  skills/
    mail-health-collect/
      SKILL.md
    daily-report-render/
      SKILL.md
    obsidian-publish-report/
      SKILL.md
```

---

## 1) `.opencode/skills/mail-health-collect/SKILL.md`

`````md
---
name: mail-health-collect
description: Query Oracle antsdb.ants_email and return a compact JSON health snapshot (sent/pending/oldest/throughput) for the last N hours.
---

# Goal
Collect mail-sender health metrics from `antsdb.ants_email` using the DB MCP and output a JSON object.

# Inputs
- `window_hours` (default 6)

# Notes
- **시간은 LLM이 추측하지 않도록** DB에서 KST 시간을 같이 조회해서 `ts`로 넣습니다.
- 아래 쿼리들은 모두 **단일 값(1 row)** 을 반환해야 합니다.

# Queries (Oracle)
아래 순서대로 실행하고 결과 숫자/문자열을 모으세요.

0) now_kst (KST 현재 시각)
```sql
SELECT TO_CHAR(SYSTIMESTAMP AT TIME ZONE 'Asia/Seoul',
               'YYYY-MM-DD"T"HH24:MI:SS') AS now_kst
FROM dual;
```

1) created_window (최근 N시간 생성)
```sql
SELECT COUNT(*) AS created_window
FROM ants_email
WHERE create_date >= SYSDATE - (:window_hours/24);
```

2) sent_window (최근 N시간 발송 완료)
```sql
SELECT COUNT(*) AS sent_window
FROM ants_email
WHERE send_flag = 'Y'
  AND send_date >= SYSDATE - (:window_hours/24);
```

3) pending_now (현재 미발송)
```sql
SELECT COUNT(*) AS pending_now
FROM ants_email
WHERE send_flag = 'N';
```

4) oldest_pending_minutes (현재 미발송 중 최장 대기 분)
```sql
SELECT NVL(ROUND((SYSDATE - MIN(create_date)) * 24 * 60), 0) AS oldest_pending_minutes
FROM ants_email
WHERE send_flag = 'N';
```

5) sent_15m (최근 15분 발송 완료)
```sql
SELECT COUNT(*) AS sent_15m
FROM ants_email
WHERE send_flag = 'Y'
  AND send_date >= SYSDATE - (15/(24*60));
```

6) pending_created_15m (최근 15분 생성분 중 아직 미발송)
```sql
SELECT COUNT(*) AS pending_created_15m
FROM ants_email
WHERE create_date >= SYSDATE - (15/(24*60))
  AND send_flag = 'N';
```

# Derive status (deterministic rules)
아래는 코드/에이전트가 **룰로** 계산하세요.

- `fail_open_loop_suspect` := (sent_15m == 0 AND pending_created_15m > 0)

Status rules (tune later):
- ERROR if `oldest_pending_minutes >= 30` OR `pending_now >= 500` OR `fail_open_loop_suspect = true`
- WARN  if `oldest_pending_minutes >= 10` OR `pending_now >= 100`
- OK   otherwise

# Output JSON (exact shape)
Return **ONLY** valid JSON with this exact shape:

```json
{
  "ts": "<now_kst>",
  "tz": "Asia/Seoul",
  "window_hours": 6,
  "mail": {
    "created_window": 0,
    "sent_window": 0,## 2) `.opencode/skills/daily-report-render/SKILL.md`

````md
---
name: daily-report-render
description: Turn health JSON (mail + optionally other systems) into a short, consistent Markdown report for morning/lunch/evening.
---

# Goal
Given the JSON snapshot from collectors, produce a Markdown report that is 10-second readable.

# Inputs
- `slot`: "morning" | "lunch" | "evening"
- `snapshot_json`: JSON object (from mail-health-collect, plus others later)

# Output
Return ONLY Markdown.

# Report template (keep stable)
**중요:** 현재 시각을 새로 만들지 말고, `snapshot_json.ts`를 그대로 사용하세요.

Use this structure:

# Daily Health Report (<slot>) - <snapshot_json.ts> (KST)

## Summary
- Mail: ✅/⚠️/🔴 한 줄 요약

## Mail (antsdb.ants_email)
- window: last <window_hours>h
- created: <created_window>
- sent: <sent_window>
- pending now: <pending_now>
- oldest pending: <oldest_pending_minutes> min
- sent (15m): <sent_15m>
- pending created (15m): <pending_created_15m>

### Verdict
- Status: OK/WARN/ERROR
- Reasons: bullet list (max 3)
- If WARN/ERROR: “What to check next” (max 3 short bullets)

# Style rules
- Use emojis only for the status line (✅⚠️🔴).
- Keep the whole report under ~30 lines.
- Never invent numbers. Use snapshot_json only.
- If `created_window == 0` and `pending_now == 0`, do NOT call it an incident.
`````

---

## 3) `.opencode/skills/obsidian-publish-report/SKILL.md`WARN/ERROR

* Reasons: bullet list (max 3)
* If WARN/ERROR: “What to check next” (max 3 short bullets)

# Style rules

* Use emojis only for the status line (✅⚠️🔴).
* Keep the whole report under ~30 lines.
* Never invent numbers. Use snapshot_json only.

````

---

## 3) `.opencode/skills/obsidian-publish-report/SKILL.md`

```md
---
name: obsidian-publish-report
description: Save a Markdown report into Obsidian using the Obsidian MCP (date-based path, append-friendly).
---

# Goal
Write the rendered Markdown into Obsidian as a dated note.

# Inputs
- `slot`: morning|lunch|evening
- `report_md`: Markdown string
- `base_dir`: (default) "Reports/Daily"

# File naming
- Path: <base_dir>/<YYYY-MM-DD>.md
- Append a section for each run:
  "## <HH:mm> (<slot>)" + report body

# Tools
Use Obsidian MCP write/append tool (server-name prefix applies).

# Behavior
- If the daily file exists: append
- If not: create then append
- Return a short confirmation with the final path (one line).
````
