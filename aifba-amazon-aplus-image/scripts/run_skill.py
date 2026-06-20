#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import time
import urllib.error
import urllib.request
import uuid
import zipfile
from typing import Any


DEFAULT_SKILL = "aifba-amazon-aplus-image"
TERMINAL_STATUSES = {"succeeded", "failed", "cancelled", "refunded"}


def parse_key_value_options(values: list[str]) -> dict[str, Any]:
    options: dict[str, Any] = {}
    for raw in values:
        if "=" not in raw:
            raise SystemExit(f"invalid --option value: {raw!r}; expected key=value")
        key, value = raw.split("=", 1)
        if not key.strip():
            raise SystemExit("invalid --option value: empty key")
        options[key.strip()] = value.strip()
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
    headers = {"Accept": "application/json", "Authorization": f"Bearer {api_key}"}
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


def safe_extract(archive: Path, target_dir: Path) -> list[str]:
    extracted: list[str] = []
    root = target_dir.resolve()
    with zipfile.ZipFile(archive) as bundle:
        for item in bundle.infolist():
            destination = (target_dir / item.filename).resolve()
            if destination != root and root not in destination.parents:
                raise SystemExit("AIFBA artifact contained an unsafe file path")
            if item.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(item) as source, destination.open("wb") as output:
                shutil.copyfileobj(source, output)
            extracted.append(str(destination))
    return extracted


def download_artifacts(response: dict[str, Any], *, api_key: str, output_dir: Path) -> None:
    run_id = str(response.get("run_id") or "run")
    run_dir = output_dir.expanduser().resolve() / run_id
    for artifact in response.get("artifacts") or []:
        if not isinstance(artifact, dict) or not artifact.get("url"):
            continue
        name = Path(str(artifact.get("name") or "aifba-result")).name
        run_dir.mkdir(parents=True, exist_ok=True)
        destination = run_dir / name
        req = urllib.request.Request(
            str(artifact["url"]),
            headers={"Authorization": f"Bearer {api_key}"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as source, destination.open("wb") as output:
                shutil.copyfileobj(source, output)
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            artifact["download_error"] = str(exc)
            continue
        artifact["local_path"] = str(destination)
        if zipfile.is_zipfile(destination):
            artifact["local_files"] = safe_extract(destination, run_dir / "images")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate optimized Amazon A+ images with AIFBA.")
    parser.add_argument("--product-url", default="", help="Amazon.com product URL.")
    parser.add_argument("--asin", default="", help="Amazon ASIN.")
    parser.add_argument("--language", default="en", help="Output language, such as en or zh.")
    parser.add_argument("--competitor-url", action="append", default=[], help="Optional competitor URL. Repeatable.")
    parser.add_argument("--option", action="append", default=[], help="Extra option as key=value. Repeatable.")
    parser.add_argument("--output-dir", default="aifba-results", help="Directory for downloaded images.")
    parser.add_argument("--idempotency-key", default="", help="Stable idempotency key for retries.")
    parser.add_argument("--no-poll", action="store_true", help="Return immediately after creating the run.")
    parser.add_argument("--timeout-seconds", type=int, default=1800, help="Polling timeout.")
    args = parser.parse_args()

    api_key = os.getenv("AIFBA_SKILL_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Set AIFBA_SKILL_API_KEY before running this skill.")
    api_base = os.getenv("AIFBA_API_BASE", "https://api.aifba.xyz/api/v1").rstrip("/")
    options = parse_key_value_options(args.option)
    options["competitor_urls"] = [item.strip() for item in args.competitor_url if item.strip()]
    payload = {
        "skill": DEFAULT_SKILL,
        "input": {
            "marketplace": "US",
            "language": args.language.strip() or "en",
            "product_url": args.product_url.strip() or None,
            "asin": args.asin.strip().upper() or None,
            "options": options,
        },
        "client": {"name": "codex", "version": "aifba-skill-0.2"},
    }
    idem = args.idempotency_key.strip() or f"{DEFAULT_SKILL}:{uuid.uuid4()}"
    response = request_json(
        "POST",
        f"{api_base}/skills/runs",
        api_key=api_key,
        payload=payload,
        idempotency_key=idem,
    )
    if not args.no_poll:
        deadline = time.time() + max(60, args.timeout_seconds)
        while str(response.get("status") or "").lower() not in TERMINAL_STATUSES and time.time() < deadline:
            time.sleep(int(response.get("poll_after_seconds") or 8))
            response = request_json("GET", f"{api_base}/skills/runs/{response['run_id']}", api_key=api_key)
        if response.get("artifacts"):
            download_artifacts(response, api_key=api_key, output_dir=Path(args.output_dir))
    json.dump(response, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
