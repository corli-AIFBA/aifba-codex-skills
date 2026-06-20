---
name: aifba-amazon-competitor
description: Use when the user wants AIFBA server-side Amazon competitor analysis, positioning gaps, review pattern analysis, or competitor-backed listing actions from an Amazon.com product URL, ASIN, or competitor ASIN list in Codex. Calls the AIFBA Skills API with the user's API key and returns competitor findings, gaps, next actions, report URL, and status URL.
---

# AIFBA Amazon Competitor

## Workflow

1. Require `AIFBA_SKILL_API_KEY` in the environment. Never print, store, or echo the API key.
2. Extract the user's Amazon.com product URL or 10-character ASIN. Add known competitors with repeated `--competitor-asin`.
3. Run `scripts/run_skill.py`.
4. Return `codex_result`, `report_url`, `status_url`, `points`, and `public_error_message` if present.
5. If the response status is not terminal, tell the user the run is still processing and provide `status_url`. Do not invent competitor findings.

## Commands

Use a product URL:

```bash
python scripts/run_skill.py --product-url "https://www.amazon.com/dp/B0XXXXXXXX"
```

Use a baseline ASIN with competitor ASINs:

```bash
python scripts/run_skill.py --asin "B0XXXXXXXX" --competitor-asin "B0YYYYYYYY" --competitor-asin "B0ZZZZZZZZ"
```

Useful options:

- `--keyword "target keyword"` for focused comparison
- `--language en` or `--language zh`
- `--no-poll` to create the task and return immediately
- `--timeout-seconds 900` for longer polling

## Result Rules

Return competitor summaries, gaps, review signals, and next actions from `codex_result`. Do not expose internal file paths, object storage keys, provider names, fallback details, cost metadata, API keys, raw prompts, or internal model routing. If the API returns only a pending result, report that pending state and the next polling URL.
