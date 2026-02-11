---
name: run-daily-health-report
description: Wrapper skill that runs collect -> render -> publish for the daily health report (mail first; extend later).
---


# Goal
한 번의 호출로 아래 3단계를 순서대로 수행하고, 최종적으로 Obsidian에 보고서를 저장합니다.


1) `mail-health-collect`
2) `daily-report-render`
3) `obsidian-publish-report`


# Inputs
- `slot`: "morning" | "lunch" | "evening" (required)
- `window_hours`: number (default 6)
- `base_dir`: string (default "Reports/Daily")


# Steps (must follow exactly)
1) `mail-health-collect`를 `window_hours`로 실행해 `snapshot_json`을 얻는다.
- 반환 JSON의 `ts`는 DB(now_kst) 기반이어야 한다.


2) `daily-report-render`를 실행한다.
- inputs: `slot`, `snapshot_json`
- 출력: `report_md` (Markdown)


3) `obsidian-publish-report`를 실행한다.
- inputs: `slot`, `report_md`, `base_dir`
- 출력: 최종 저장 경로/확인 메시지


# Output
Return ONLY JSON:


```json
{
"slot": "morning|lunch|evening",
"ts": "<snapshot_json.ts>",
"status": "OK|WARN|ERROR",
"obsidian_result": "<one-line confirmation or final path>",
"summary": "<one short line>"
}
