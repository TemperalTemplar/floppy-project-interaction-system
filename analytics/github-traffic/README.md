# GitHub Traffic Archive

This directory preserves repository-traffic observations that GitHub otherwise exposes only through a rolling recent window.

## Purpose

The archive exists to preserve historical evidence of Floppy repository discovery and acquisition without treating traffic counts as proof of individual human users.

GitHub traffic metrics may include human activity and automated activity. In particular, `unique_cloners` must not be described as a confirmed count of unique people.

## Collection

The scheduled workflow `.github/workflows/collect-github-traffic.yml` runs once per day and can also be started manually with `workflow_dispatch`.

The collector is `tools/collect_github_traffic.py`.

The collector reads these GitHub traffic endpoints using the repository secret `TRAFFIC_TOKEN`:

- views;
- clones;
- popular referrers;
- popular paths.

`TRAFFIC_TOKEN` is read-only for traffic collection and is never written into this archive. Repository writes use the temporary GitHub Actions `GITHUB_TOKEN` with `contents: write` permission.

## Files

- `baseline/2026-08-11.json` — administrator-recorded initial 14-day GitHub Insights snapshot.
- `snapshots/YYYY-MM-DD.json` — raw API snapshot for each automated collection date.
- `daily-history.csv` — merged per-day views, unique visitors, clones, and unique cloners recovered from successive API windows.
- `rolling-summary-history.csv` — one row per collection date containing the API's rolling totals at that time.
- `referrers-history.jsonl` — dated snapshots of popular referrers.
- `popular-content-history.jsonl` — dated snapshots of popular repository paths.

## Interpretation

`daily-history.csv` and `rolling-summary-history.csv` answer different questions.

A daily row describes traffic GitHub attributed to one calendar day. A rolling-summary row describes the total visible in GitHub's recent traffic window at the time of collection. They must not be added together as though they were independent events.

The initial baseline was copied by the administrator from GitHub Insights on August 11, 2026. It records 72 views, 3 unique visitors, 162 clones, and 77 unique cloners for GitHub's then-current 14-day window, along with the visible referrer and popular-content table.
