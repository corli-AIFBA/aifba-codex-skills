---
name: aifba-amazon-title
description: Use when the user wants AIFBA server-side Amazon title or listing copy optimization from an Amazon.com product URL or ASIN in Codex. Calls the AIFBA Skills API with the user's API key and returns optimized titles, listing highlights, partial rationale, report URL, and status URL.
---

# AIFBA Amazon Title

## Workflow

1. Require `AIFBA_SKILL_API_KEY` in the environment. Never print, store, or echo the API key.
2. Extract an Amazon.com product URL or 10-character ASIN from the user request. Ask for one only if neither is available.
3. Run `scripts/run_skill.py` with the product input and any target keywords.
4. Return the API response fields that matter to the user: `codex_result`, `report_url`, `status_url`, `points`, and `public_error_message` if present.
5. If the response status is not terminal, tell the user the run is still processing and provide `status_url`. Do not invent optimization results.

## Commands

Use a product URL:

```bash
python scripts/run_skill.py --product-url "https://www.amazon.com/dp/B0XXXXXXXX" --keyword "main keyword"
```

Use an ASIN:

```bash
python scripts/run_skill.py --asin "B0XXXXXXXX" --keyword "main keyword"
```

Useful options:

- `--language en` or `--language zh`
- `--option title_limit=180`
- `--no-poll` to create the task and return immediately
- `--timeout-seconds 900` for longer polling

## Result Rules

Return the optimized title candidates and visible rationale from `codex_result`. Do not expose internal file paths, object storage keys, provider names, fallback details, cost metadata, API keys, raw prompts, or internal model routing. If the API returns only a pending result, report that pending state and the next polling URL.
