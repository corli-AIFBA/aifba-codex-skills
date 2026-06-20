#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
import urllib.error
import urllib.request
from typing import Any


DEFAULT_SKILL = "aifba-amazon-bullets"
TERMINAL_STATUSES = {"succeeded", "failed", "cancelled", "refunded"}


def parse_key_value_options(values: list[str]) -> dict[str, Any]:
    options: dict[str, Any] = {}
    for raw in values:
        if "=" not in raw:
            raise SystemExit(f"invalid --option value: {raw!r}; expected key=value")
        key, value = raw.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit("invalid --option value: empty key")
        options[key] = value.strip()
    return options


def request_json(
    method: str,
    url: str,
    *,
    api_key: str,
    payload: dict[str, Any] | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    data = None
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            text = response.read().decode("utf-8")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"AIFBA API error {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"AIFBA API request failed: {exc}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an AIFBA Codex Skill.")
    parser.add_argument("--product-url", default="", help="Amazon.com product URL.")
    parser.add_argument("--asin", default="", help="Amazon ASIN.")
    parser.add_argument("--marketplace", default="US", help="Marketplace. Currently US only.")
    parser.add_argument("--language", default="en", help="Output language, such as en or zh.")
    parser.add_argument("--keyword", action="append", default=[], help="Target keyword. Repeatable.")
    parser.add_argument("--option", action="append", default=[], help="Extra option as key=value. Repeatable.")
    parser.add_argument("--idempotency-key", default="", help="Stable idempotency key for retries.")
    parser.add_argument("--no-poll", action="store_true", help="Return immediately after creating the run.")
    parser.add_argument("--timeout-seconds", type=int, default=600, help="Polling timeout.")
    args = parser.parse_args()

    api_key = os.getenv("AIFBA_SKILL_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Set AIFBA_SKILL_API_KEY before running this skill.")
    api_base = os.getenv("AIFBA_API_BASE", "https://api.aifba.xyz/api/v1").rstrip("/")
    idem = args.idempotency_key.strip() or f"{DEFAULT_SKILL}:{uuid.uuid4()}"
    payload = {
        "skill": DEFAULT_SKILL,
        "input": {
            "marketplace": args.marketplace.strip() or "US",
            "language": args.language.strip() or "en",
            "product_url": args.product_url.strip() or None,
            "asin": args.asin.strip().upper() or None,
            "keywords": [item.strip() for item in args.keyword if item.strip()],
            "options": parse_key_value_options(args.option),
        },
        "client": {"name": "codex", "version": "aifba-skill-0.2"},
    }
    response = request_json(
        "POST",
        f"{api_base}/skills/runs",
        api_key=api_key,
        payload=payload,
        idempotency_key=idem,
    )
    if not args.no_poll:
        deadline = time.time() + max(30, args.timeout_seconds)
        while str(response.get("status") or "").lower() not in TERMINAL_STATUSES and time.time() < deadline:
            time.sleep(int(response.get("poll_after_seconds") or 8))
            response = request_json("GET", f"{api_base}/skills/runs/{response['run_id']}", api_key=api_key)
    json.dump(response, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
