---
name: aifba-amazon-aplus-image
description: Use when the user wants AIFBA to generate optimized Amazon A+ images from an Amazon.com product URL or ASIN in Codex. Calls the AIFBA Skills API, waits for the server-side task, downloads and extracts generated image files, and returns A+ image briefs, local image paths, report URL, and status.
---

# AIFBA Amazon A+ Image

## Workflow

1. Require `AIFBA_SKILL_API_KEY` in the environment. Never print, store, or echo it.
2. Extract an Amazon.com product URL or 10-character ASIN. Ask for one only if neither is available.
3. Run `scripts/run_skill.py`. Add competitor URLs only when the user provides them.
4. Return `codex_result`, generated image files from `artifacts[].local_files`, `report_url`, `status_url`, and `points`.
5. Display the generated images in Codex when the client supports local image rendering. Do not return only a web link.

## Commands

```bash
python scripts/run_skill.py --asin "B0XXXXXXXX" --language zh
```

```bash
python scripts/run_skill.py --product-url "https://www.amazon.com/dp/B0XXXXXXXX" \
  --option visual_style=premium --option overall_design=conversion-focused
```

Generated files are saved under `aifba-results/<run_id>/images/` in the current workspace.

## Result Rules

Do not expose server file paths, object storage keys, provider names, fallback details, cost metadata, API keys, raw prompts, or internal model routing. Local downloaded paths are user-owned result paths and may be returned.
