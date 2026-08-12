#!/usr/bin/env python3
"""Archive GitHub repository traffic metrics into durable repository history."""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API_VERSION = "2022-11-28"
ROOT = Path("analytics/github-traffic")
SNAPSHOT_DIR = ROOT / "snapshots"
DAILY_HISTORY = ROOT / "daily-history.csv"
ROLLING_HISTORY = ROOT / "rolling-summary-history.csv"
REFERRERS_HISTORY = ROOT / "referrers-history.jsonl"
POPULAR_HISTORY = ROOT / "popular-content-history.jsonl"


def api_get(repository: str, token: str, suffix: str) -> Any:
    url = f"https://api.github.com/repos/{repository}{suffix}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "floppy-github-traffic-collector",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API request failed for {suffix}: HTTP {exc.code}: {body}"
        ) from exc


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def merge_daily_history(views: dict[str, Any], clones: dict[str, Any]) -> None:
    rows: dict[str, dict[str, str]] = {}

    if DAILY_HISTORY.exists():
        with DAILY_HISTORY.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                rows[row["date"]] = row

    for item in views.get("views", []):
        date = item["timestamp"][:10]
        row = rows.setdefault(
            date,
            {
                "date": date,
                "views": "",
                "unique_visitors": "",
                "clones": "",
                "unique_cloners": "",
            },
        )
        row["views"] = str(item["count"])
        row["unique_visitors"] = str(item["uniques"])

    for item in clones.get("clones", []):
        date = item["timestamp"][:10]
        row = rows.setdefault(
            date,
            {
                "date": date,
                "views": "",
                "unique_visitors": "",
                "clones": "",
                "unique_cloners": "",
            },
        )
        row["clones"] = str(item["count"])
        row["unique_cloners"] = str(item["uniques"])

    DAILY_HISTORY.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["date", "views", "unique_visitors", "clones", "unique_cloners"]
    with DAILY_HISTORY.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for date in sorted(rows):
            writer.writerow(rows[date])


def upsert_rolling_summary(
    collected_at: str,
    collection_date: str,
    views: dict[str, Any],
    clones: dict[str, Any],
) -> None:
    rows: dict[str, dict[str, str]] = {}
    if ROLLING_HISTORY.exists():
        with ROLLING_HISTORY.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                rows[row["collection_date"]] = row

    rows[collection_date] = {
        "collection_date": collection_date,
        "collected_at_utc": collected_at,
        "views_14d": str(views.get("count", 0)),
        "unique_visitors_14d": str(views.get("uniques", 0)),
        "clones_14d": str(clones.get("count", 0)),
        "unique_cloners_14d": str(clones.get("uniques", 0)),
    }

    ROLLING_HISTORY.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "collection_date",
        "collected_at_utc",
        "views_14d",
        "unique_visitors_14d",
        "clones_14d",
        "unique_cloners_14d",
    ]
    with ROLLING_HISTORY.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for date in sorted(rows):
            writer.writerow(rows[date])


def upsert_jsonl(path: Path, collection_date: str, record: dict[str, Any]) -> None:
    records: dict[str, dict[str, Any]] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            existing = json.loads(line)
            records[existing["collection_date"]] = existing

    records[collection_date] = record
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for date in sorted(records):
            handle.write(json.dumps(records[date], sort_keys=True) + "\n")


def main() -> int:
    repository = os.environ.get("GITHUB_REPOSITORY", "").strip()
    token = os.environ.get("TRAFFIC_TOKEN", "").strip()

    if not repository:
        print("ERROR: GITHUB_REPOSITORY is not set.", file=sys.stderr)
        return 2
    if not token:
        print("ERROR: TRAFFIC_TOKEN is not set.", file=sys.stderr)
        return 2

    now = utc_now()
    collected_at = now.isoformat().replace("+00:00", "Z")
    collection_date = now.date().isoformat()

    views = api_get(repository, token, "/traffic/views")
    clones = api_get(repository, token, "/traffic/clones")
    referrers = api_get(repository, token, "/traffic/popular/referrers")
    popular = api_get(repository, token, "/traffic/popular/paths")

    snapshot = {
        "schema_version": "1.0",
        "repository": repository,
        "collection_date": collection_date,
        "collected_at_utc": collected_at,
        "source": "GitHub REST traffic API",
        "window_note": "GitHub traffic endpoints expose a rolling recent window; this snapshot preserves what the API returned at collection time.",
        "views": views,
        "clones": clones,
        "referrers": referrers,
        "popular_content": popular,
    }
    write_json(SNAPSHOT_DIR / f"{collection_date}.json", snapshot)

    merge_daily_history(views, clones)
    upsert_rolling_summary(collected_at, collection_date, views, clones)
    upsert_jsonl(
        REFERRERS_HISTORY,
        collection_date,
        {
            "collection_date": collection_date,
            "collected_at_utc": collected_at,
            "referrers": referrers,
        },
    )
    upsert_jsonl(
        POPULAR_HISTORY,
        collection_date,
        {
            "collection_date": collection_date,
            "collected_at_utc": collected_at,
            "popular_content": popular,
        },
    )

    print(
        "Traffic collection complete: "
        f"{views.get('count', 0)} views / {views.get('uniques', 0)} unique visitors; "
        f"{clones.get('count', 0)} clones / {clones.get('uniques', 0)} unique cloners."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
