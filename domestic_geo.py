#!/usr/bin/env python3
"""Evidence-bounded domestic GEO collector using Tencent WSA + selectable LLMs."""

import argparse
import datetime as dt
import getpass
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "config.json"


class GeoError(RuntimeError):
    pass


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def keychain_secret(service: str, account: Optional[str] = None) -> Optional[str]:
    if sys.platform != "darwin":
        return None
    account = account or os.getenv("GEO_KEYCHAIN_ACCOUNT") or getpass.getuser()
    result = subprocess.run(
        ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def get_secret(env_name: str, keychain_service: str) -> Optional[str]:
    return os.getenv(env_name) or keychain_secret(keychain_service)


def post_json(url: str, payload: Dict[str, Any], headers: Dict[str, str], timeout: int) -> Dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:1200]
        raise GeoError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise GeoError(f"网络请求失败: {exc.reason}") from exc
    except (TimeoutError, socket.timeout) as exc:
        raise GeoError(f"网络请求超时: {timeout} 秒") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GeoError(f"接口返回的不是 JSON: {raw[:500]}") from exc


def normalize_search_response(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    response = raw.get("Response", raw)
    if response.get("Error"):
        error = response["Error"]
        raise GeoError(f"腾讯搜索错误 {error.get('Code', 'unknown')}: {error.get('Message', '')}")
    pages = response.get("Pages")
    if not isinstance(pages, list):
        raise GeoError("腾讯搜索响应缺少 Pages")
    results = []
    for index, item in enumerate(pages, start=1):
        if isinstance(item, str):
            try:
                item = json.loads(item)
            except json.JSONDecodeError:
                item = {"passage": item}
        if not isinstance(item, dict):
            continue
        results.append(
            {
                "id": f"S{index}",
                "position": index,
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "site": item.get("site", ""),
                "published_at": item.get("date", ""),
                "passage": re.sub(r"<[^>]+>", "", item.get("passage", "")),
                "score": item.get("score"),
            }
        )
    return results


def search_wsa(config: Dict[str, Any], query: str, api_key: str) -> Dict[str, Any]:
    search = config["search"]
    payload = {"Query": query, "Mode": search.get("mode", 0)}
    count = int(search.get("results_per_prompt", 10))
    if count != 10:
        payload["Cnt"] = count
    raw = post_json(
        search["endpoint"],
        payload,
        {"Authorization": f"Bearer {api_key}"},
        int(search.get("timeout_seconds", 45)),
    )
    return {"raw": raw, "results": normalize_search_response(raw)}


def evidence_text(results: List[Dict[str, Any]]) -> str:
    blocks = []
    for item in results:
        blocks.append(
            "\n".join(
                [
                    f"[{item['id']}] 排序位置: {item['position']}",
                    f"标题: {item['title']}",
                    f"站点: {item['site']}",
                    f"URL: {item['url']}",
                    f"发布时间: {item['published_at']}",
                    f"摘要: {item['passage']}",
                ]
            )
        )
    return "\n\n".join(blocks)


def provider_config(config: Dict[str, Any], provider_id: Optional[str] = None) -> Dict[str, Any]:
    """Resolve a configured provider while keeping legacy config.json files usable."""
    if "models" not in config:
        model = dict(config["model"])
        model.setdefault("id", "deepseek")
        model.setdefault("label", "DeepSeek API")
        model.setdefault("env_key", "DEEPSEEK_API_KEY")
        model.setdefault("keychain_service", "codex-deepseek-api-key")
        model.setdefault("extra_payload", {"thinking": {"type": "disabled"}})
        return model
    selected = provider_id or config.get("default_model_provider")
    if not selected:
        raise GeoError("未指定模型供应商，且配置缺少 default_model_provider")
    try:
        model = dict(config["models"][selected])
    except KeyError as exc:
        available = ", ".join(sorted(config["models"]))
        raise GeoError(f"未知模型供应商 {selected}；可选：{available}") from exc
    model["id"] = selected
    return model


def active_question_set(config: Dict[str, Any]) -> Dict[str, Any]:
    """Return the immutable active question-set snapshot; support old prompt lists read-only."""
    question_sets = config.get("question_sets")
    if not question_sets:
        prompts = config.get("prompts")
        if not isinstance(prompts, list) or not prompts:
            raise GeoError("配置缺少 question_sets，且没有可兼容的 prompts")
        questions = [
            {
                "id": f"legacy-{index:03d}",
                "track": "benchmark",
                "intent": "legacy",
                "text": prompt,
                "tags": [],
                "enabled": True,
            }
            for index, prompt in enumerate(prompts, start=1)
        ]
        snapshot = {
            "id": "legacy-unversioned",
            "status": "legacy",
            "language": "unknown",
            "market": "unknown",
            "questions": questions,
        }
        snapshot["fingerprint"] = question_set_fingerprint(snapshot)
        return snapshot

    active_id = question_sets.get("active_version")
    versions = question_sets.get("versions")
    if not active_id or not isinstance(versions, list):
        raise GeoError("question_sets 必须包含 active_version 和 versions")
    matches = [item for item in versions if item.get("id") == active_id]
    if len(matches) != 1:
        raise GeoError(f"active_version {active_id} 必须精确匹配一个问题集版本")
    snapshot = json.loads(json.dumps(matches[0], ensure_ascii=False))
    validate_question_set(snapshot)
    snapshot["fingerprint"] = question_set_fingerprint(snapshot)
    return snapshot


def validate_question_set(question_set: Dict[str, Any]) -> None:
    questions = question_set.get("questions")
    if not isinstance(questions, list) or not questions:
        raise GeoError(f"问题集 {question_set.get('id', 'unknown')} 没有问题")
    seen = set()
    enabled_count = 0
    for question in questions:
        question_id = str(question.get("id", "")).strip()
        text = str(question.get("text", "")).strip()
        track = question.get("track")
        if not question_id or not text:
            raise GeoError("每个问题必须包含非空 id 和 text")
        if question_id in seen:
            raise GeoError(f"问题ID重复：{question_id}")
        if track not in ("benchmark", "discovery"):
            raise GeoError(f"问题 {question_id} 的 track 必须是 benchmark 或 discovery")
        seen.add(question_id)
        enabled_count += bool(question.get("enabled", True))
    if enabled_count == 0:
        raise GeoError("活动问题集至少需要一个已启用问题")


def question_set_fingerprint(question_set: Dict[str, Any]) -> str:
    """Hash comparison-critical fields so silent edits cannot extend an old trend."""
    comparable = {
        "id": question_set.get("id"),
        "language": question_set.get("language"),
        "market": question_set.get("market"),
        "questions": [
            {
                "id": item.get("id"),
                "track": item.get("track"),
                "intent": item.get("intent"),
                "text": item.get("text"),
                "tags": item.get("tags", []),
                "enabled": item.get("enabled", True),
            }
            for item in question_set.get("questions", [])
        ],
    }
    raw = json.dumps(comparable, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def active_questions(question_set: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [item for item in question_set["questions"] if item.get("enabled", True)]


def run_settings_snapshot(config: Dict[str, Any], model: Dict[str, Any]) -> Dict[str, Any]:
    """Keep useful reproducibility fields without storing credentials or headers."""
    return {
        "model_provider": model["id"],
        "model_name": model["name"],
        "temperature": model.get("temperature", 0),
        "max_tokens": model.get("max_tokens", 2200),
        "model_timeout_seconds": model.get("timeout_seconds", 90),
        "search_provider": "tencent_wsa",
        "search_mode": config["search"].get("mode", 0),
        "search_results_per_prompt": config["search"].get("results_per_prompt", 10),
        "search_timeout_seconds": config["search"].get("timeout_seconds", 45),
        "thinking": model.get("extra_payload", {}).get("thinking", {"type": "not_configured"}),
    }


def usage_metadata(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize token counters returned by OpenAI-compatible providers."""
    usage = raw.get("usage")
    if not isinstance(usage, dict):
        return {}
    allowed = ("prompt_tokens", "completion_tokens", "total_tokens", "input_tokens", "output_tokens")
    return {key: usage[key] for key in allowed if isinstance(usage.get(key), (int, float))}


def classify_error(error: str) -> str:
    """Map provider-specific error text to a stable user-facing result state."""
    normalized = error.casefold()
    if "超时" in error or "timed out" in normalized or "timeout" in normalized:
        return "timeout"
    if "http 429" in normalized or "rate limit" in normalized or "too many requests" in normalized or "限流" in error:
        return "rate_limited"
    if "未返回约定的结构化 json" in normalized or "不是 json" in normalized or "解析" in error:
        return "parse_error"
    if "unauthorized" in normalized or "forbidden" in normalized or "http 401" in normalized or "http 403" in normalized:
        return "api_error"
    return "api_error"


def model_answer(model: Dict[str, Any], prompt: str, results: List[Dict[str, Any]], api_key: str) -> Dict[str, Any]:
    system = """你是严谨的品牌可见度研究助手。只能使用用户给出的搜索证据回答，不得补写证据中没有的企业能力、认证、规格、服务或效果。证据不足时明确写“公开证据不足”。输出必须是一个 JSON 对象，不要使用代码围栏，字段为：answer_markdown（字符串）、recommended_entities（数组，每项含 name、rank、evidence_ids）、citations_used（实际使用的证据编号数组）。rank 必须是回答中的明确推荐顺序；没有形成明确推荐列表时 recommended_entities 为空数组。每个事实后使用 [S1] 形式引用。"""
    user = f"问题：{prompt}\n\n搜索证据：\n{evidence_text(results)}"
    payload = {
        "model": model["name"],
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": model.get("temperature", 0),
        "max_tokens": model.get("max_tokens", 2200),
        "response_format": {"type": "json_object"},
    }
    payload.update(model.get("extra_payload", {}))
    raw = post_json(
        model["endpoint"],
        payload,
        {"Authorization": f"Bearer {api_key}"},
        int(model.get("timeout_seconds", 90)),
    )
    try:
        content = raw["choices"][0]["message"]["content"]
        if isinstance(content, str) and content.strip().startswith("```"):
            content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE)
        parsed = json.loads(content)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise GeoError(f"{model.get('label', model['id'])} 未返回约定的结构化 JSON") from exc
    return {"raw": raw, "parsed": parsed}


def canonical_domain(url: str) -> str:
    host = urllib.parse.urlparse(url).hostname or ""
    return host.lower().removeprefix("www.")


def brand_aliases(config: Dict[str, Any]) -> List[str]:
    """Return the customer-configured brand names in display order without duplicates."""
    values = [config["brand"].get("name", ""), *config["brand"].get("aliases", [])]
    aliases = []
    seen = set()
    for value in values:
        alias = str(value).strip()
        normalized = unicodedata.normalize("NFKC", alias).casefold()
        if alias and normalized not in seen:
            aliases.append(alias)
            seen.add(normalized)
    return aliases


def brand_profile_snapshot(config: Dict[str, Any]) -> Dict[str, Any]:
    """Keep customer-declared business context separate from measured model answers."""
    brand = config["brand"]
    return {
        "name": str(brand.get("name", "")).strip(),
        "aliases": brand_aliases(config)[1:],
        "business_description": str(brand.get("business_description", "")).strip(),
        "core_offerings": [str(item).strip() for item in brand.get("core_offerings", []) if str(item).strip()],
        "primary_markets": [str(item).strip() for item in brand.get("primary_markets", []) if str(item).strip()],
        "official_website": str(brand.get("official_website", "")).strip(),
        "headquarters": str(brand.get("headquarters", "")).strip(),
        "official_channels": [str(item).strip() for item in brand.get("official_channels", []) if str(item).strip()],
        "official_domains": [str(item).strip() for item in brand.get("official_domains", []) if str(item).strip()],
    }


def alias_spans(text: str, alias: str) -> List[tuple]:
    """Find an alias while preventing short Latin aliases from matching inside other words."""
    if not text or not alias:
        return []
    normalized_text = unicodedata.normalize("NFKC", text)
    normalized_alias = unicodedata.normalize("NFKC", alias)
    is_latin = bool(re.search(r"[A-Za-z0-9]", normalized_alias)) and not bool(
        re.search(r"[\u3400-\u9fff]", normalized_alias)
    )
    escaped = re.escape(normalized_alias)
    pattern = rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])" if is_latin else escaped
    return [(match.start(), match.end()) for match in re.finditer(pattern, normalized_text, flags=re.IGNORECASE)]


def alias_script_group(alias: str) -> str:
    """Group configured names for market diagnostics without asking customers for extra fields."""
    normalized = unicodedata.normalize("NFKC", alias)
    if re.search(r"[\u3400-\u9fff]", normalized):
        return "zh"
    if re.search(r"[A-Za-z]", normalized):
        return "en"
    return "other"


def brand_match_details(config: Dict[str, Any], text: str) -> Dict[str, Any]:
    """Expose every matched customer-entered name so the UI can show how a mention was counted."""
    normalized_text = unicodedata.normalize("NFKC", str(text))
    cues = config["brand"].get(
        "negative_context_cues",
        ["不推荐", "不是", "未提及", "没有提到", "未列出", "不包括", "无关"],
    )
    matched_aliases = []
    counts: Dict[str, int] = {}
    snippets = []
    negative_context = []
    negative_mentions = 0
    mention_count = 0
    for alias in brand_aliases(config):
        spans = alias_spans(normalized_text, alias)
        if not spans:
            continue
        matched_aliases.append(alias)
        counts[alias] = len(spans)
        mention_count += len(spans)
        for start, end in spans:
            snippet = normalized_text[max(0, start - 18) : min(len(normalized_text), end + 18)].strip()
            if snippet not in snippets and len(snippets) < 5:
                snippets.append(snippet)
            matched_cues = [cue for cue in cues if cue and cue in snippet]
            if matched_cues:
                negative_mentions += 1
                negative_context.append({"alias": alias, "cues": matched_cues, "snippet": snippet})
    return {
        "mentioned": bool(matched_aliases),
        "matched_aliases": matched_aliases,
        "matched_chinese_aliases": [alias for alias in matched_aliases if alias_script_group(alias) == "zh"],
        "matched_english_aliases": [alias for alias in matched_aliases if alias_script_group(alias) == "en"],
        "chinese_name_mentioned": any(alias_script_group(alias) == "zh" for alias in matched_aliases),
        "english_name_mentioned": any(alias_script_group(alias) == "en" for alias in matched_aliases),
        "alias_mention_counts": counts,
        "mention_count": mention_count,
        "mention_snippets": snippets,
        "negative_context": negative_context,
        "negative_only": mention_count > 0 and negative_mentions == mention_count,
    }


def entity_matches_brand(config: Dict[str, Any], entity_name: str) -> bool:
    return brand_match_details(config, entity_name)["mentioned"]


def find_brand_rank(config: Dict[str, Any], answer: Dict[str, Any]) -> Optional[int]:
    ranks = []
    for entity in answer.get("recommended_entities", []):
        name = str(entity.get("name", ""))
        if entity_matches_brand(config, name):
            try:
                ranks.append(int(entity["rank"]))
            except (KeyError, TypeError, ValueError):
                pass
    return min(ranks) if ranks else None


def score_answer(config: Dict[str, Any], answer: Dict[str, Any], results: List[Dict[str, Any]]) -> Dict[str, Any]:
    text = str(answer.get("answer_markdown", ""))
    match = brand_match_details(config, text)
    mentioned = match["mentioned"]
    rank = find_brand_rank(config, answer) if mentioned else None
    valid_ids = {item["id"] for item in results}
    used_ids = [item for item in answer.get("citations_used", []) if item in valid_ids]
    used_results = [item for item in results if item["id"] in used_ids]
    domains = sorted({canonical_domain(item["url"]) for item in used_results if item.get("url")})
    official_domains = {domain.casefold() for domain in config["brand"]["official_domains"]}
    official_cited = any(domain in official_domains or any(domain.endswith("." + official) for official in official_domains) for domain in domains)
    identity_evidence = []
    if official_cited:
        identity_evidence.append("official_domain_cited")
    if config["brand"].get("name") in match["matched_aliases"]:
        identity_evidence.append("full_company_name")
    text_folded = unicodedata.normalize("NFKC", text).casefold()
    matched_offerings = [
        offering
        for offering in config["brand"].get("core_offerings", [])
        if str(offering).strip() and unicodedata.normalize("NFKC", str(offering)).casefold() in text_folded
    ] if mentioned else []
    if matched_offerings:
        identity_evidence.append("business_context")
    identity_match_status = "not_applicable" if not mentioned else ("supported" if identity_evidence else "alias_only")
    if not mentioned:
        score = 0.0
    else:
        weights = config["scoring"]
        rank_component = 40.0 if rank is None else max(0.0, 100.0 - (rank - 1) * 10.0)
        citation_component = min(100.0, len(used_ids) * 20.0)
        official_component = 100.0 if official_cited else 0.0
        score = round(
            rank_component * weights["rank_weight"]
            + citation_component * weights["citation_weight"]
            + official_component * weights["official_source_weight"],
            2,
        )
    return {
        "brand_mentioned": mentioned,
        "matched_aliases": match["matched_aliases"],
        "matched_chinese_aliases": match["matched_chinese_aliases"],
        "matched_english_aliases": match["matched_english_aliases"],
        "chinese_name_mentioned": match["chinese_name_mentioned"],
        "english_name_mentioned": match["english_name_mentioned"],
        "alias_mention_counts": match["alias_mention_counts"],
        "mention_count": match["mention_count"],
        "mention_snippets": match["mention_snippets"],
        "negative_context": match["negative_context"],
        "negative_only": match["negative_only"],
        "brand_rank": rank,
        "visibility_score": score,
        "citations_used": used_ids,
        "citation_domains": domains,
        "official_domain_cited": official_cited,
        "identity_match_status": identity_match_status,
        "identity_evidence": identity_evidence,
        "matched_business_context": matched_offerings,
        "scoring_method": config["scoring"]["name"],
    }


def citation_metadata(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Keep citation locations, but do not persist provider-returned passage text."""
    keys = ("id", "position", "title", "url", "site", "published_at", "score")
    return [{key: item.get(key) for key in keys} for item in results]


def build_summary(records: List[Dict[str, Any]], scoring_name: str) -> Dict[str, Any]:
    available = [record for record in records if record["status"] == "ok"]
    unavailable = [record for record in records if record["status"] != "ok"]
    mentioned = [record for record in available if record["metrics"]["brand_mentioned"]]
    chinese_mentioned = [
        record
        for record in available
        if record["metrics"].get(
            "chinese_name_mentioned",
            any(alias_script_group(alias) == "zh" for alias in record["metrics"].get("matched_aliases", [])),
        )
    ]
    english_mentioned = [
        record
        for record in available
        if record["metrics"].get(
            "english_name_mentioned",
            any(alias_script_group(alias) == "en" for alias in record["metrics"].get("matched_aliases", [])),
        )
    ]
    ranked = [record["metrics"]["brand_rank"] for record in mentioned if record["metrics"]["brand_rank"] is not None]
    domains = sorted({domain for record in available for domain in record["metrics"]["citation_domains"]})
    state_counts: Dict[str, int] = {}
    for record in records:
        state = record.get("result_state")
        if not state:
            if record.get("status") == "ok":
                state = "mentioned" if record.get("metrics", {}).get("brand_mentioned") else "not_mentioned"
            else:
                state = "unavailable"
        state_counts[state] = state_counts.get(state, 0) + 1
    return {
        "scoring_method": scoring_name,
        "prompt_count": len(records),
        "available_count": len(available),
        "unavailable_count": len(unavailable),
        "mention_rate_percent": round(len(mentioned) * 100 / len(available), 2) if available else None,
        "chinese_name_mention_rate_percent": round(len(chinese_mentioned) * 100 / len(available), 2) if available else None,
        "english_name_mention_rate_percent": round(len(english_mentioned) * 100 / len(available), 2) if available else None,
        "average_rank": round(sum(ranked) / len(ranked), 2) if ranked else None,
        "average_visibility_score": round(sum(record["metrics"]["visibility_score"] for record in available) / len(available), 2) if available else None,
        "unique_citation_domain_count": len(domains),
        "citation_domains": domains,
        "result_state_counts": state_counts,
    }


def report_markdown(run: Dict[str, Any]) -> str:
    summary = run["summary"]
    question_set = run.get("question_set", {})
    settings = run.get("run_settings", {})
    lines = [
        f"# 国内 GEO 采集报告 · {run['run_date']}",
        "",
        f"- 状态：{run['status']}",
        f"- 运行编号：`{run.get('run_id', 'legacy')}`",
        f"- 模型：`{settings.get('model_provider', run.get('model_provider', 'unavailable'))}` / `{settings.get('model_name', run.get('model_name', 'unavailable'))}`",
        f"- 问题集版本：`{question_set.get('id', 'legacy-unversioned')}`",
        f"- 问题集指纹：`{question_set.get('fingerprint', 'unavailable')}`",
        f"- 可用回答：{summary['available_count']} / {summary['prompt_count']}",
        f"- 品牌提及率：{summary['mention_rate_percent'] if summary['mention_rate_percent'] is not None else 'unavailable'}",
        f"- 中文名称提及率：{summary.get('chinese_name_mention_rate_percent', 'unavailable')}",
        f"- 英文名称提及率：{summary.get('english_name_mention_rate_percent', 'unavailable')}",
        f"- 平均排名：{summary['average_rank'] if summary['average_rank'] is not None else 'unavailable'}",
        f"- 平均透明复现分：{summary['average_visibility_score'] if summary['average_visibility_score'] is not None else 'unavailable'}",
        f"- 评分方法：`{summary['scoring_method']}`",
        f"- 结果状态：`{json.dumps(summary.get('result_state_counts', {}), ensure_ascii=False)}`",
        "",
        f"> 本报告基于配置的联网搜索 API + {run.get('model_label', run.get('model_name', 'LLM API'))}。它不是消费端模型界面的完全等价回放；透明复现分只代表本项目公开公式。",
        "> 搜索引用只证明“模型看到了什么”，不证明页面内容真实。当前结果含多篇低权威聚合/营销页，其中涉及产能、认证、客户案例、厂房、专利和服务能力的陈述均为待核模型输出，不得直接对外使用。",
        "",
    ]
    for index, record in enumerate(run["records"], start=1):
        lines.extend(
            [
                f"## {index}. {record['prompt']}",
                "",
                f"- 问题ID：`{record.get('question_id', 'legacy')}`",
                f"- 轨道：`{record.get('question_track', 'benchmark')}`",
                f"- 状态：{record['status']}",
                f"- 结果状态：`{record.get('result_state', 'legacy')}`",
                f"- 耗时：{record.get('elapsed_ms', 'unavailable')} ms",
                f"- Token：{record.get('usage', {}).get('total_tokens', 'unavailable')}",
                "",
            ]
        )
        if record["status"] == "ok":
            metrics = record["metrics"]
            lines.extend(
                [
                    f"- 品牌提及：{'是' if metrics['brand_mentioned'] else '否'}",
                    f"- 中文名称提及：{'是' if metrics.get('chinese_name_mentioned') else '否'}",
                    f"- 英文名称提及：{'是' if metrics.get('english_name_mentioned') else '否'}",
                    f"- 命中名称：{', '.join(metrics.get('matched_aliases', [])) or '-'}",
                    f"- 推荐排名：{metrics['brand_rank'] if metrics['brand_rank'] is not None else '-'}",
                    f"- 透明复现分：{metrics['visibility_score']}",
                    f"- 官网被引用：{'是' if metrics['official_domain_cited'] else '否'}",
                    f"- 品牌身份判断：{metrics.get('identity_match_status', 'unavailable')}",
                    f"- 身份佐证：{', '.join(metrics.get('identity_evidence', [])) or '-'}",
                    "",
                    record["answer"]["answer_markdown"],
                    "",
                ]
            )
            used_ids = set(metrics.get("citations_used", []))
            used_citations = [item for item in record.get("search_citations", []) if item.get("id") in used_ids]
            if used_citations:
                lines.extend(["### 本题实际使用的搜索来源", ""])
                for item in used_citations:
                    title = item.get("title") or item.get("site") or item.get("url") or item.get("id")
                    lines.append(f"- [{item.get('id')}] [{title}]({item.get('url')})")
                lines.append("")
        else:
            lines.extend([f"原因：{record.get('error', 'unavailable')}", ""])
    return "\n".join(lines)


def run_collection(
    config_path: Path,
    output_root: Path,
    resume_path: Optional[Path] = None,
    provider_id: Optional[str] = None,
) -> int:
    config = read_json(config_path)
    question_set = active_question_set(config)
    questions = active_questions(question_set)
    wsa_key = get_secret("TENCENTCLOUD_WSA_APIKEY", "codex-tencent-wsa-api-key")
    model = provider_config(config, provider_id)
    model_key = get_secret(model["env_key"], model["keychain_service"])
    if not wsa_key:
        raise GeoError("缺少腾讯联网搜索 API KEY；请设置环境变量或 macOS 钥匙串 codex-tencent-wsa-api-key")
    if not model_key:
        raise GeoError(
            f"缺少 {model.get('label', model['id'])} API KEY；"
            f"请设置 {model['env_key']} 或 macOS 钥匙串 {model['keychain_service']}"
        )

    now = dt.datetime.now().astimezone()
    run_dir = output_root / now.strftime("%Y-%m-%d") / now.strftime("%H%M%S")
    run_id = f"{now.strftime('%Y%m%dT%H%M%S%z')}-{model['id']}"
    prior_by_prompt: Dict[str, Dict[str, Any]] = {}
    if resume_path:
        prior = read_json(resume_path)
        prior_question_set = prior.get("question_set", {})
        if (
            prior_question_set.get("id") == question_set["id"]
            and prior_question_set.get("fingerprint") == question_set["fingerprint"]
        ):
            prior_by_prompt = {
                record["question_id"]: record
                for record in prior.get("records", [])
                if record.get("status") == "ok" and record.get("question_id")
            }
    records = []
    fatal_upstream_error: Optional[str] = None
    for index, question in enumerate(questions, start=1):
        prompt = question["text"]
        question_id = question["id"]
        if question_id in prior_by_prompt:
            records.append(prior_by_prompt[question_id])
            continue
        record: Dict[str, Any] = {
            "question_id": question_id,
            "question_track": question["track"],
            "question_intent": question.get("intent"),
            "question_tags": question.get("tags", []),
            "prompt": prompt,
            "status": "unavailable",
        }
        started_at = time.monotonic()
        if fatal_upstream_error:
            record["error"] = f"未继续调用：{fatal_upstream_error}"
            record["result_state"] = "upstream_unavailable"
            record["elapsed_ms"] = 0
            records.append(record)
            continue
        try:
            search = search_wsa(config, prompt, wsa_key)
            answer = model_answer(model, prompt, search["results"], model_key)
            metrics = score_answer(config, answer["parsed"], search["results"])
            record.update(
                {
                    "status": "ok",
                    "search_citations": citation_metadata(search["results"]),
                    "answer": answer["parsed"],
                    "metrics": metrics,
                    "usage": usage_metadata(answer["raw"]),
                    "result_state": "mentioned" if metrics["brand_mentioned"] else "not_mentioned",
                }
            )
            write_json(run_dir / "raw" / f"{index:02d}-model.json", answer["raw"])
        except GeoError as exc:
            record["error"] = str(exc)
            record["result_state"] = classify_error(record["error"])
            if any(code in record["error"] for code in ("UnauthorizedOperation", "ResourceNotFound", "ResourceUnavailable")):
                fatal_upstream_error = record["error"]
        record["elapsed_ms"] = round((time.monotonic() - started_at) * 1000)
        records.append(record)

    summary = build_summary(records, config["scoring"]["name"])
    status = "complete" if summary["unavailable_count"] == 0 else "partial"
    run = {
        "run_id": run_id,
        "run_at": now.isoformat(),
        "run_date": now.strftime("%Y-%m-%d"),
        "status": status,
        "model_provider": model["id"],
        "model_name": model["name"],
        "model_label": model.get("label", model["id"]),
        "run_settings": run_settings_snapshot(config, model),
        "brand_profile": brand_profile_snapshot(config),
        "question_set": {
            "id": question_set["id"],
            "fingerprint": question_set["fingerprint"],
            "language": question_set.get("language"),
            "market": question_set.get("market"),
            "benchmark_count": sum(item["track"] == "benchmark" for item in questions),
            "discovery_count": sum(item["track"] == "discovery" for item in questions),
        },
        "source_layers": ["tencent_wsa_search", f"{model['id']}_api", "local_transparent_scoring"],
        "summary": summary,
        "records": records,
    }
    write_json(run_dir / "report.json", run)
    (run_dir / "report.md").write_text(report_markdown(run), encoding="utf-8")
    print(str(run_dir / "report.md"))
    return 0 if status == "complete" else 2


def doctor() -> int:
    config = read_json(DEFAULT_CONFIG) if DEFAULT_CONFIG.exists() else {}
    question_set_ok = False
    question_set_info: Dict[str, Any] = {}
    try:
        question_set = active_question_set(config)
        question_set_ok = True
        question_set_info = {
            "id": question_set["id"],
            "fingerprint": question_set["fingerprint"],
            "enabled_questions": len(active_questions(question_set)),
        }
    except GeoError as exc:
        question_set_info = {"error": str(exc)}
    model_checks = {}
    for provider_id, model in config.get("models", {}).items():
        model_checks[provider_id] = bool(get_secret(model["env_key"], model["keychain_service"]))
    if not model_checks:
        model_checks["deepseek"] = bool(get_secret("DEEPSEEK_API_KEY", "codex-deepseek-api-key"))
    checks = {
        "python": sys.version.split()[0],
        "config": DEFAULT_CONFIG.exists(),
        "brand_profile": {
            "name": bool(config.get("brand", {}).get("name")),
            "business_description": bool(config.get("brand", {}).get("business_description")),
            "core_offerings": len(config.get("brand", {}).get("core_offerings", [])),
            "primary_markets": len(config.get("brand", {}).get("primary_markets", [])),
            "official_website": bool(config.get("brand", {}).get("official_website")),
            "headquarters": bool(config.get("brand", {}).get("headquarters")),
        },
        "question_set": question_set_info,
        "model_keys": model_checks,
        "tencent_wsa_key": bool(get_secret("TENCENTCLOUD_WSA_APIKEY", "codex-tencent-wsa-api-key")),
    }
    print(json.dumps(checks, ensure_ascii=False, indent=2))
    return 0 if all([checks["config"], question_set_ok, checks["tencent_wsa_key"], all(model_checks.values())]) else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("doctor", help="检查配置和凭据是否齐全")
    subparsers.add_parser("questions", help="显示当前问题集版本、指纹和已启用问题")
    run_parser = subparsers.add_parser("run", help="运行全部监控问题")
    run_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    run_parser.add_argument("--output", type=Path, default=ROOT / "runs")
    run_parser.add_argument("--resume", type=Path, help="复用上一报告中已成功的问题，仅重试 unavailable 项")
    run_parser.add_argument("--provider", help="模型供应商 ID；默认使用 config.json 的 default_model_provider")
    render_parser = subparsers.add_parser("render", help="从 report.json 重新生成同目录 report.md")
    render_parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "doctor":
            return doctor()
        if args.command == "questions":
            config = read_json(DEFAULT_CONFIG)
            question_set = active_question_set(config)
            output = {
                "id": question_set["id"],
                "fingerprint": question_set["fingerprint"],
                "language": question_set.get("language"),
                "market": question_set.get("market"),
                "questions": active_questions(question_set),
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
            return 0
        if args.command == "render":
            run = read_json(args.report)
            output = args.report.with_name("report.md")
            output.write_text(report_markdown(run), encoding="utf-8")
            print(str(output))
            return 0
        return run_collection(args.config, args.output, args.resume, args.provider)
    except GeoError as exc:
        print(f"unavailable: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
