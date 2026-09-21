#!/usr/bin/env python3
"""Loopback-only dashboard server with a small monitoring-config API."""

import argparse
import ipaddress
import json
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

import build_web_data
import domestic_geo as geo
import monitoring_runner


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
CONFIG_PATH = ROOT / "config.json"


def is_loopback_host(value: str) -> bool:
    """Reject DNS rebinding and cross-origin writes to the local configuration API."""
    if not value:
        return False
    try:
        hostname = urlparse(f"//{value}").hostname
    except ValueError:
        return False
    if hostname == "localhost":
        return True
    try:
        return ipaddress.ip_address(hostname or "").is_loopback
    except ValueError:
        return False


def is_allowed_origin(value: str) -> bool:
    if not value:
        return True
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and is_loopback_host(parsed.netloc)


def validate_monitoring_payload(payload: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    cadence = str(payload.get("cadence", "daily"))
    if cadence not in {"daily", "weekly", "manual"}:
        raise geo.GeoError("监控节奏必须是 daily、weekly 或 manual")
    time_text = str(payload.get("time", "09:00"))
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", time_text):
        raise geo.GeoError("执行时间必须是 HH:MM")
    try:
        weekday = int(payload.get("weekday", 0))
    except (TypeError, ValueError) as exc:
        raise geo.GeoError("每周执行日必须是0到6") from exc
    if weekday not in range(7):
        raise geo.GeoError("每周执行日必须是0到6")
    providers = payload.get("providers") or []
    if not isinstance(providers, list) or not providers:
        raise geo.GeoError("至少选择一个模型")
    available = config.get("models", {})
    unknown = [provider for provider in providers if provider not in available]
    if unknown:
        raise geo.GeoError(f"包含未知模型：{', '.join(unknown)}")
    return {
        "enabled": bool(payload.get("enabled", False)),
        "cadence": cadence,
        "time": time_text,
        "timezone": "Asia/Shanghai",
        "weekday": weekday,
        "providers": providers,
        "scheduler_status": config.get("monitoring", {}).get("scheduler_status", "not_installed"),
    }


def public_monitoring_config(config: Dict[str, Any]) -> Dict[str, Any]:
    plan = monitoring_runner.monitoring_plan(config)
    labels = {provider: config["models"][provider].get("label", provider) for provider in plan["providers"]}
    return {
        **plan,
        "schedulerStatus": plan["scheduler_status"],
        "questionCount": plan["question_count"],
        "plannedModelCalls": plan["planned_model_calls"],
        "plannedSearchCalls": plan["planned_search_calls"],
        "modelLabels": labels,
    }


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def request_is_local(self, require_origin: bool = False) -> bool:
        try:
            client_is_local = ipaddress.ip_address(self.client_address[0]).is_loopback
        except ValueError:
            client_is_local = False
        if not client_is_local or not is_loopback_host(self.headers.get("Host", "")):
            return False
        return not require_origin or is_allowed_origin(self.headers.get("Origin", ""))

    def do_GET(self) -> None:
        if not self.request_is_local():
            self.send_json(403, {"error": "local_requests_only"})
            return
        request_path = urlparse(self.path).path
        if request_path == "/api/monitoring":
            try:
                self.send_json(200, public_monitoring_config(geo.read_json(CONFIG_PATH)))
            except geo.GeoError as exc:
                self.send_json(400, {"error": str(exc)})
            return
        if request_path == "/assets/logo.png":
            body = (ROOT / "assets" / "logo.png").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if request_path == "/assets/community-wechat.jpg":
            body = (ROOT / "assets" / "community-wechat.jpg").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if request_path == "/PROVIDERS.md":
            body = (ROOT / "PROVIDERS.md").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self) -> None:
        if not self.request_is_local(require_origin=True):
            self.send_json(403, {"error": "local_same_origin_requests_only"})
            return
        if urlparse(self.path).path != "/api/monitoring":
            self.send_json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 65536:
                raise geo.GeoError("请求大小无效")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise geo.GeoError("请求必须是JSON对象")
            config = geo.read_json(CONFIG_PATH)
            config["monitoring"] = validate_monitoring_payload(payload, config)
            temporary = CONFIG_PATH.with_suffix(".json.tmp")
            geo.write_json(temporary, config)
            temporary.replace(CONFIG_PATH)
            build_web_data.main()
            self.send_json(200, {"saved": True, "monitoring": public_monitoring_config(config)})
        except (geo.GeoError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": str(exc)})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4187)
    args = parser.parse_args()
    if args.host not in {"127.0.0.1", "localhost"}:
        raise SystemExit("安全限制：配置接口只能绑定到本机回环地址")
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"http://{args.host}:{args.port}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
