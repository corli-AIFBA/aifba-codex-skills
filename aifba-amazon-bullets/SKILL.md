---
name: aifba-amazon-bullets
description: Use when the user wants AIFBA server-side Amazon five-bullet or Item Highlights optimization from an Amazon.com product URL or ASIN in Codex. Calls the AIFBA Skills API and returns optimized bullets, visible rationale, report URL, and status URL.
---

# AIFBA Amazon Bullets

## Workflow

1. Require `AIFBA_SKILL_API_KEY` in the environment. Never print, store, or echo the API key.
2. Extract an Amazon.com product URL or 10-character ASIN. Ask for one only if neither is available.
3. Run `scripts/run_skill.py` with the product input and optional target keywords.
4. Return `codex_result`, `report_url`, `status_url`, `points`, and `public_error_message` if present.
5. Return the optimized bullets and the visible optimization rationale. Do not invent missing results.

## Commands

```bash
python scripts/run_skill.py --asin "B0XXXXXXXX" --keyword "main keyword"
```

```bash
python scripts/run_skill.py --product-url "https://www.amazon.com/dp/B0XXXXXXXX" --language zh
```

## Result Rules

Do not expose internal file paths, object storage keys, provider names, fallback details, cost metadata, API keys, raw prompts, or internal model routing.
