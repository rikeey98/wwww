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
