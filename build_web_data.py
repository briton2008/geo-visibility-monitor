#!/usr/bin/env python3
"""Build the static dashboard dataset from local GEO run reports."""

import json
from collections import defaultdict
from pathlib import Path
from typing import Optional

import domestic_geo as geo


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "web" / "answer-data.js"


def all_reports(root: Path = ROOT) -> list:
    reports = []
    for path in root.glob("**/report.json"):
        run = geo.read_json(path)
        provider = run.get("model_provider") or run.get("run_settings", {}).get("model_provider")
        if not provider:
            provider = "deepseek" if "deepseek" in str(run.get("model_name", "")).casefold() else "legacy-unknown"
        reports.append({"provider": provider, "path": path, "run": run})
    return reports


def latest_complete_reports(reports: Optional[list] = None) -> list:
    latest = {}
    for item in reports if reports is not None else all_reports():
        run = item["run"]
        if run.get("status") != "complete":
            continue
        provider = item["provider"]
        run_at = run.get("run_at", "")
        if provider not in latest or run_at > latest[provider]["run"].get("run_at", ""):
            latest[provider] = item
    return [latest[key] for key in sorted(latest)]


def question_set_compatible(run: dict, active: dict) -> bool:
    snapshot = run.get("question_set", {})
    if snapshot.get("fingerprint"):
        return snapshot.get("id") == active["id"] and snapshot.get("fingerprint") == active["fingerprint"]
    run_prompts = [record.get("prompt") for record in run.get("records", [])]
    active_prompts = [question["text"] for question in geo.active_questions(active)]
    return run_prompts == active_prompts


def recomputed_records(config: dict, run: dict) -> list:
    records = []
    for record in run.get("records", []):
        copied = dict(record)
        if record.get("status") == "ok":
            copied["metrics"] = geo.score_answer(
                config,
                record.get("answer", {}),
                record.get("search_citations", []),
            )
        records.append(copied)
    return records


def point_from_runs(config: dict, date: str, items: list) -> dict:
    records = []
    for item in items:
        records.extend(recomputed_records(config, item["run"]))
    summary = geo.build_summary(records, config["scoring"]["name"])
    return {
        "date": date,
        "providerCount": len({item["provider"] for item in items}),
        "runCount": len(items),
        "answerCount": summary["prompt_count"],
        "availableCount": summary["available_count"],
        "unavailableCount": summary["unavailable_count"],
        "mentionRate": summary["mention_rate_percent"],
        "chineseMentionRate": summary["chinese_name_mention_rate_percent"],
        "englishMentionRate": summary["english_name_mention_rate_percent"],
        "averageRank": summary["average_rank"],
        "averageScore": summary["average_visibility_score"],
    }


def build_trends(config: dict, reports: list) -> tuple[list, dict]:
    active = geo.active_question_set(config)
    latest_by_provider_day = {}
    for item in reports:
        run = item["run"]
        if run.get("status") != "complete" or not question_set_compatible(run, active):
            continue
        date = run.get("run_date") or str(run.get("run_at", ""))[:10]
        key = (item["provider"], date)
        if key not in latest_by_provider_day or run.get("run_at", "") > latest_by_provider_day[key]["run"].get("run_at", ""):
            latest_by_provider_day[key] = item

    by_day = defaultdict(list)
    by_provider_day = defaultdict(lambda: defaultdict(list))
    for (provider, date), item in latest_by_provider_day.items():
        by_day[date].append(item)
        by_provider_day[provider][date].append(item)

    overall = [point_from_runs(config, date, by_day[date]) for date in sorted(by_day)]
    per_provider = {
        provider: [point_from_runs(config, date, dates[date]) for date in sorted(dates)]
        for provider, dates in sorted(by_provider_day.items())
    }
    return overall, per_provider


def history_rows(config: dict, reports: list) -> list:
    rows = []
    for item in reports:
        run = item["run"]
        records = recomputed_records(config, run)
        summary = geo.build_summary(records, config["scoring"]["name"])
        rows.append(
            {
                "runId": run.get("run_id", item["path"].parent.name),
                "runAt": run.get("run_at"),
                "runDate": run.get("run_date") or str(run.get("run_at", ""))[:10],
                "provider": item["provider"],
                "modelLabel": run.get("model_label") or run.get("model_name") or item["provider"],
                "status": run.get("status", "unavailable"),
                "availableCount": summary["available_count"],
                "promptCount": summary["prompt_count"],
                "mentionRate": summary["mention_rate_percent"],
                "averageRank": summary["average_rank"],
                "averageScore": summary["average_visibility_score"],
                "questionSetId": run.get("question_set", {}).get("id", "legacy-prompt-match"),
            }
        )
    return sorted(rows, key=lambda row: row.get("runAt") or "", reverse=True)[:100]


def build_rows(root: Path = ROOT) -> dict:
    config = geo.read_json(root / "config.json")
    plan = config.get("monitoring", {})
    allowed_providers = set(plan.get("providers") or config.get("models", {}))
    reports = [item for item in all_reports(root) if item["provider"] in allowed_providers]
    rows = []
    providers = []
    for item in latest_complete_reports(reports):
        path, run, provider = item["path"], item["run"], item["provider"]
        label = run.get("model_label") or run.get("model_name") or provider
        providers.append({"id": provider, "label": label})
        for record in recomputed_records(config, run):
            metrics = record.get("metrics", {})
            answer = record.get("answer", {})
            citations = record.get("search_citations", [])
            rows.append(
                {
                    "id": f"{provider}:{record.get('question_id', len(rows) + 1)}",
                    "runAt": run.get("run_at"),
                    "runId": run.get("run_id", path.parent.name),
                    "modelProvider": provider,
                    "modelName": run.get("model_name") or run.get("run_settings", {}).get("model_name") or provider,
                    "modelLabel": label,
                    "questionId": record.get("question_id", "legacy"),
                    "questionTrack": record.get("question_track", "benchmark"),
                    "prompt": record.get("prompt", ""),
                    "status": record.get("status", "unavailable"),
                    "resultState": record.get("result_state") or (
                        "mentioned" if metrics.get("brand_mentioned") else "not_mentioned"
                    ),
                    "elapsedMs": record.get("elapsed_ms"),
                    "usage": record.get("usage", {}),
                    "metrics": metrics,
                    "answerMarkdown": answer.get("answer_markdown", ""),
                    "citations": citations,
                }
            )
    providers.sort(key=lambda provider: provider["label"])
    trends, model_trends = build_trends(config, reports)
    active = geo.active_question_set(config)
    return {
        "generatedAt": geo.dt.datetime.now().astimezone().isoformat(),
        "source": "local report.json files; latest complete report per provider for answer records and latest comparable report per provider/day for trends",
        "questionSet": {"id": active["id"], "fingerprint": active["fingerprint"]},
        "providerCount": len(providers),
        "recordCount": len(rows),
        "providers": providers,
        "records": rows,
        "trend": trends,
        "modelTrend": model_trends,
        "batchHistory": history_rows(config, reports),
        "monitoringPlan": {
            "enabled": bool(plan.get("enabled", False)),
            "cadence": plan.get("cadence", "daily"),
            "time": plan.get("time", "09:00"),
            "timezone": plan.get("timezone", "Asia/Shanghai"),
            "weekday": int(plan.get("weekday", 0)),
            "providers": plan.get("providers", sorted(config.get("models", {}))),
            "questionSetId": active["id"],
            "schedulerStatus": plan.get("scheduler_status", "not_installed"),
        },
    }


def main() -> None:
    payload = json.dumps(build_rows(), ensure_ascii=False, separators=(",", ":"))
    OUTPUT.write_text(f"window.GEO_ANSWER_DATA={payload};\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
