좋아. 지금 구조 기준으로 **그대로 복붙해서 쓰는 3줄 프롬프트** 줄게.

---

### 🔹 아침 보고서 실행용 (3줄)

```
1) mail-health-collect를 window_hours=6으로 실행해서 JSON을 생성해.
2) 그 JSON을 daily-report-render에 slot="morning"으로 넘겨서 Markdown 보고서를 만들어.
3) 그 Markdown을 obsidian-publish-report에 base_dir="Reports/Daily"로 저장해.
```

---

### 🔹 점심이면

```
1) mail-health-collect를 window_hours=6으로 실행해서 JSON을 생성해.
2) 그 JSON을 daily-report-render에 slot="lunch"로 넘겨서 Markdown 보고서를 만들어.
3) 그 Markdown을 obsidian-publish-report에 base_dir="Reports/Daily"로 저장해.
```

---

### 🔹 저녁이면

```
1) mail-health-collect를 window_hours=6으로 실행해서 JSON을 생성해.
2) 그 JSON을 daily-report-render에 slot="evening"으로 넘겨서 Markdown 보고서를 만들어.
3) 그 Markdown을 obsidian-publish-report에 base_dir="Reports/Daily"로 저장해.
```

---

이게 제일 안정적인 호출 방식이야.
(중간 JSON을 명시적으로 넘기라고 하는 게 중요함)

실행해보고:

* 정상 저장됨
* 중간 JSON 안 넘어감
* 스킬 체인 꼬임

중 뭐가 나오는지 알려줘.
그다음 바로 래퍼 스킬로 깔끔하게 묶어버리자.
