#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
import os
from pathlib import Path
import shutil
import ssl
import sys
import time
import urllib.error
import urllib.request
import uuid
from typing import Any

try:
    import certifi
except ImportError:
    certifi = None


TERMINAL_STATUSES = {"succeeded", "failed", "cancelled", "refunded"}
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/137.0.0.0 Safari/537.36"
)


def urlopen_with_defaults(req: urllib.request.Request, *, timeout: int):
    context = None
    if certifi is not None:
        try:
            context = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            context = None
    if context is not None:
        return urllib.request.urlopen(req, timeout=timeout, context=context)
    return urllib.request.urlopen(req, timeout=timeout)


def request_json(method: str, url: str, *, api_key: str) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": DEFAULT_USER_AGENT,
        },
        method=method,
    )
    try:
        with urlopen_with_defaults(req, timeout=60) as response:
            text = response.read().decode("utf-8")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"AIFBA API error {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"AIFBA API request failed: {exc}") from exc


def multipart_body(files: dict[str, Path], *, boundary: str) -> bytes:
    chunks: list[bytes] = []
    for field_name, path in files.items():
        if not path.is_file():
            raise SystemExit(f"report file not found: {path}")
        media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        chunks.extend(
            [
                f"--{boundary}\r\n".encode(),
                (
                    f'Content-Disposition: form-data; name="{field_name}"; '
                    f'filename="{path.name}"\r\n'
                ).encode(),
                f"Content-Type: {media_type}\r\n\r\n".encode(),
                path.read_bytes(),
                b"\r\n",
            ]
        )
    chunks.extend(
        [
            f"--{boundary}\r\n".encode(),
            b'Content-Disposition: form-data; name="client_name"\r\n\r\n',
            b"codex\r\n",
            f"--{boundary}\r\n".encode(),
            b'Content-Disposition: form-data; name="client_version"\r\n\r\n',
            b"aifba-skill-0.2\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )
    return b"".join(chunks)


def create_run(
    url: str,
    *,
    api_key: str,
    files: dict[str, Path],
    idempotency_key: str,
) -> dict[str, Any]:
    boundary = f"aifba-{uuid.uuid4().hex}"
    data = multipart_body(files, boundary=boundary)
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Idempotency-Key": idempotency_key,
            "User-Agent": DEFAULT_USER_AGENT,
        },
        method="POST",
    )
    try:
        with urlopen_with_defaults(req, timeout=180) as response:
            text = response.read().decode("utf-8")
            return json.loads(text) if text else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"AIFBA API error {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"AIFBA API request failed: {exc}") from exc


def download_artifacts(response: dict[str, Any], *, api_key: str, output_dir: Path) -> None:
    run_id = str(response.get("run_id") or "run")
    run_dir = output_dir.expanduser().resolve() / run_id
    for artifact in response.get("artifacts") or []:
        if not isinstance(artifact, dict) or not artifact.get("url"):
            continue
        run_dir.mkdir(parents=True, exist_ok=True)
        destination = run_dir / Path(str(artifact.get("name") or "aifba-ads-diagnosis.xlsx")).name
        req = urllib.request.Request(
            str(artifact["url"]),
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": DEFAULT_USER_AGENT,
            },
            method="GET",
        )
        try:
            with urlopen_with_defaults(req, timeout=180) as source, destination.open("wb") as output:
                shutil.copyfileobj(source, output)
            artifact["local_path"] = str(destination)
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            artifact["download_error"] = str(exc)


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose Amazon ads reports with AIFBA.")
    parser.add_argument("--sp-report", required=True, help="Sponsored Products report file.")
    parser.add_argument("--sb-report", default="", help="Optional Sponsored Brands report file.")
    parser.add_argument("--product-report", default="", help="Optional advertised product report file.")
    parser.add_argument("--output-dir", default="aifba-results", help="Directory for the result workbook.")
    parser.add_argument("--idempotency-key", default="", help="Stable idempotency key for retries.")
    parser.add_argument("--no-poll", action="store_true", help="Return immediately after creating the run.")
    parser.add_argument("--timeout-seconds", type=int, default=900, help="Polling timeout.")
    args = parser.parse_args()

    api_key = os.getenv("AIFBA_SKILL_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Set AIFBA_SKILL_API_KEY before running this skill.")
    api_base = os.getenv("AIFBA_API_BASE", "https://api.aifba.xyz/api/v1").rstrip("/")
    files = {"sp_report": Path(args.sp_report).expanduser().resolve()}
    if args.sb_report:
        files["sb_report"] = Path(args.sb_report).expanduser().resolve()
    if args.product_report:
        files["product_report"] = Path(args.product_report).expanduser().resolve()
    idem = args.idempotency_key.strip() or f"aifba-amazon-ads-diagnosis:{uuid.uuid4()}"
    response = create_run(
        f"{api_base}/skills/runs/ads-diagnosis",
        api_key=api_key,
        files=files,
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
