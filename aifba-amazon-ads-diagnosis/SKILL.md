---
name: aifba-amazon-ads-diagnosis
description: Use when the user wants AIFBA to diagnose Amazon Sponsored Products or Sponsored Brands report files in Codex. Uploads reports to the authenticated AIFBA Skills API, returns diagnosis and prioritized actions, downloads the result workbook, and keeps the task in AIFBA history.
---

# AIFBA Amazon Ads Diagnosis

## Workflow

1. Require `AIFBA_SKILL_API_KEY` in the environment. Never print, store, or echo it.
2. Locate the user's Sponsored Products report. Accept Sponsored Brands and advertised product reports when provided.
3. Run `scripts/run_skill.py --sp-report <path>` and add optional report arguments.
4. Return `codex_result`, the workbook path from `artifacts[].local_path`, `report_url`, `status_url`, and `points`.
5. Summarize the highest-priority diagnosis in Codex. Do not return only a web link.

## Commands

```bash
python scripts/run_skill.py --sp-report "/path/to/sp-report.xlsx"
```

```bash
python scripts/run_skill.py \
  --sp-report "/path/to/sp-report.xlsx" \
  --sb-report "/path/to/sb-report.xlsx" \
  --product-report "/path/to/product-report.xlsx"
```

The result workbook is saved under `aifba-results/<run_id>/` in the current workspace.

## Result Rules

Do not expose server file paths, object storage keys, provider names, fallback details, cost metadata, API keys, raw prompts, or internal model routing. Local downloaded paths are user-owned result paths and may be returned.
