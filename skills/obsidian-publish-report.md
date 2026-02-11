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
