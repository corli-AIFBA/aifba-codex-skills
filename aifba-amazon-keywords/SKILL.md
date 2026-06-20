---
name: aifba-amazon-keywords
description: Use when the user wants AIFBA server-side Amazon keyword research, keyword gap analysis, long-tail keyword discovery, or traffic opportunity analysis from an Amazon.com product URL or ASIN in Codex. Calls the AIFBA Skills API with the user's API key and returns keyword opportunities, next actions, report URL, and status URL.
---

# AIFBA Amazon Keywords

## Workflow

1. Require `AIFBA_SKILL_API_KEY` in the environment. Never print, store, or echo the API key.
2. Extract an Amazon.com product URL or 10-character ASIN from the user request. Ask for one only if neither is available.
3. Run `scripts/run_skill.py` with the product input. Optional seed keywords can be passed with repeated `--keyword`.
4. Return `codex_result`, `report_url`, `status_url`, `points`, and `public_error_message` if present.
5. If the response status is not terminal, tell the user the run is still processing and provide `status_url`. Do not invent keyword results.

## Commands

Use a product URL:

```bash
python scripts/run_skill.py --product-url "https://www.amazon.com/dp/B0XXXXXXXX"
```

Use an ASIN and seed keywords:

```bash
python scripts/run_skill.py --asin "B0XXXXXXXX" --keyword "seed keyword" --keyword "long tail seed"
```

Useful options:

- `--language en` or `--language zh`
- `--no-poll` to create the task and return immediately
- `--timeout-seconds 900` for longer polling

## Result Rules

Return keyword opportunities, long-tail terms, gaps, and next actions from `codex_result`. Do not expose internal file paths, object storage keys, provider names, fallback details, cost metadata, API keys, raw prompts, or internal model routing. If the API returns only a pending result, report that pending state and the next polling URL.
