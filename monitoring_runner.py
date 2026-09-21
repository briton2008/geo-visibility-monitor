#!/usr/bin/env python3
"""Safe entry point for a scheduler: inspect by default, collect only with --execute."""

import argparse
import datetime as dt
import json
import os
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import build_web_data
import domestic_geo as geo


ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "state" / "monitoring-state.json"
LOCK_PATH = ROOT / "state" / "monitoring.lock"


def monitoring_plan(config: dict) -> dict:
    raw = config.get("monitoring", {})
    cadence = raw.get("cadence", "daily")
    if cadence not in {"daily", "weekly", "manual"}:
        raise geo.GeoError("轻量监控器仅支持 daily、weekly 或 manual")
    time_text = str(raw.get("time", "09:00"))
    try:
        hour, minute = [int(part) for part in time_text.split(":", 1)]
        dt.time(hour=hour, minute=minute)
    except (TypeError, ValueError) as exc:
        raise geo.GeoError("monitoring.time 必须是 HH:MM") from exc
    timezone = str(raw.get("timezone", "Asia/Shanghai"))
    try:
        ZoneInfo(timezone)
    except Exception as exc:
        raise geo.GeoError(f"无效时区：{timezone}") from exc
    providers = raw.get("providers") or sorted(config.get("models", {}))
    unknown = [provider for provider in providers if provider not in config.get("models", {})]
    if unknown:
        raise geo.GeoError(f"监控计划包含未知模型：{', '.join(unknown)}")
    try:
        weekday = int(raw.get("weekday", 0))
    except (TypeError, ValueError) as exc:
        raise geo.GeoError("monitoring.weekday 必须是0到6") from exc
    if weekday not in range(7):
        raise geo.GeoError("monitoring.weekday 必须是0到6")
    question_count = len(geo.active_questions(geo.active_question_set(config)))
    return {
        "enabled": bool(raw.get("enabled", False)),
        "cadence": cadence,
        "time": time_text,
        "timezone": timezone,
        "weekday": weekday,
        "providers": providers,
        "question_count": question_count,
        "planned_model_calls": len(providers) * question_count,
        "planned_search_calls": len(providers) * question_count,
        "scheduler_status": raw.get("scheduler_status", "not_installed"),
    }


def due_date(plan: dict, now: dt.datetime) -> Optional[str]:
    cadence = plan.get("cadence", "daily")
    if cadence == "manual":
        return None
    local = now.astimezone(ZoneInfo(plan["timezone"]))
    hour, minute = [int(part) for part in plan["time"].split(":", 1)]
    scheduled = local.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if cadence == "weekly" and local.weekday() != plan["weekday"]:
        return None
    return local.date().isoformat() if local >= scheduled else None


def is_due(plan: dict, state: dict, now: dt.datetime) -> bool:
    target = due_date(plan, now)
    return bool(plan["enabled"] and target and state.get("last_completed_date") != target)


def acquire_lock() -> int:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        return os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise geo.GeoError("已有监控批次运行中；本次不重复启动") from exc


def execute(config_path: Path, force: bool = False) -> int:
    config = geo.read_json(config_path)
    plan = monitoring_plan(config)
    state = geo.read_json(STATE_PATH) if STATE_PATH.exists() else {}
    now = dt.datetime.now(tz=dt.timezone.utc)
    if not force and not is_due(plan, state, now):
        print(json.dumps({"status": "not_due", "plan": plan}, ensure_ascii=False, indent=2))
        return 0
    lock_fd = acquire_lock()
    results = []
    try:
        for provider in plan["providers"]:
            try:
                code = geo.run_collection(
                    config_path,
                    ROOT / "runs-by-provider" / provider,
                    provider_id=provider,
                )
                results.append({"provider": provider, "status": "complete" if code == 0 else "partial"})
            except geo.GeoError as exc:
                results.append({"provider": provider, "status": "unavailable", "error": str(exc)})
        build_web_data.main()
        local_now = now.astimezone(ZoneInfo(plan["timezone"]))
        complete = all(item["status"] == "complete" for item in results)
        state = {
            "last_attempt_at": local_now.isoformat(),
            "last_completed_date": local_now.date().isoformat() if complete else state.get("last_completed_date"),
            "status": "complete" if complete else "partial",
            "providers": results,
        }
        geo.write_json(STATE_PATH, state)
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0 if complete else 2
    finally:
        os.close(lock_fd)
        LOCK_PATH.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config.json")
    parser.add_argument("--execute", action="store_true", help="实际调用搜索和模型 API")
    parser.add_argument("--force", action="store_true", help="忽略今日是否已完成；必须同时使用 --execute")
    args = parser.parse_args()
    config = geo.read_json(args.config)
    plan = monitoring_plan(config)
    if not args.execute:
        print(json.dumps({"status": "dry_run", "plan": plan}, ensure_ascii=False, indent=2))
        return 0
    return execute(args.config, force=args.force)


if __name__ == "__main__":
    raise SystemExit(main())
