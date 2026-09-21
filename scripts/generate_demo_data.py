#!/usr/bin/env python3
"""Regenerate the committed synthetic dashboard fixture."""

import datetime as dt
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "web" / "answer-data.example.js"
PROVIDERS = [{"id": f"provider-{letter}", "label": f"示例模型 {letter.upper()}"} for letter in "abcdef"]
QUESTIONS = [
    "这一品类有哪些值得了解的供应商？",
    "哪些供应商可以提供产品和应用方案？",
    "企业采购时应该比较哪些供应商？",
    "选择供应商时应该比较哪些指标？",
    "示例天然食品有限公司主要提供哪些产品和服务？",
]


def main() -> None:
    records = []
    for provider_index, provider in enumerate(PROVIDERS):
        for question_index, question in enumerate(QUESTIONS):
            mentioned = question_index in {1, 4}
            ranked = question_index == 1
            rank = provider_index % 3 + 2 if ranked else None
            score = float(72 - provider_index * 3) if ranked else (28.0 if mentioned else 0.0)
            answer = (
                "这是完全虚构的演示回答。示例品牌仅用于展示提及、排名和证据回溯界面。"
                if mentioned
                else "这是完全虚构的演示回答。本条未提及被监控的示例品牌。"
            )
            records.append({
                "id": f"{provider['id']}:q{question_index + 1}",
                "runAt": "2026-01-01T09:00:00+08:00",
                "runId": f"demo-{provider['id']}",
                "modelProvider": provider["id"],
                "modelName": provider["label"],
                "modelLabel": provider["label"],
                "questionId": f"demo-q{question_index + 1}",
                "questionTrack": "benchmark",
                "prompt": question,
                "status": "ok",
                "resultState": "mentioned" if mentioned else "not_mentioned",
                "elapsedMs": None,
                "usage": {},
                "metrics": {
                    "brand_mentioned": mentioned,
                    "matched_aliases": ["示例品牌"] if mentioned else [],
                    "matched_chinese_aliases": ["示例品牌"] if mentioned else [],
                    "matched_english_aliases": [],
                    "chinese_name_mentioned": mentioned,
                    "english_name_mentioned": False,
                    "alias_mention_counts": {"示例品牌": 1} if mentioned else {},
                    "mention_count": 1 if mentioned else 0,
                    "mention_snippets": ["示例品牌仅用于界面演示"] if mentioned else [],
                    "negative_context": [],
                    "negative_only": False,
                    "brand_rank": rank,
                    "visibility_score": score,
                    "citations_used": ["S1"] if mentioned else [],
                    "citation_domains": ["example.com"] if mentioned else [],
                    "official_domain_cited": mentioned,
                    "identity_match_status": "supported" if mentioned else "not_applicable",
                    "identity_evidence": ["official_domain_cited"] if mentioned else [],
                    "matched_business_context": ["示例产品"] if mentioned else [],
                    "scoring_method": "transparent_replica_v1",
                },
                "answerMarkdown": answer,
                "citations": [{"id": "S1", "position": 1, "title": "虚构演示来源", "url": "https://example.com/demo", "site": "example.com", "published_at": "", "score": 1.0}],
            })
    scores = [record["metrics"]["visibility_score"] for record in records]
    payload = {
        "dataClassification": "synthetic_demo",
        "generatedAt": dt.datetime(2026, 1, 1, 9, 0, tzinfo=dt.timezone(dt.timedelta(hours=8))).isoformat(),
        "source": "deterministic synthetic demo fixture; not real observations",
        "questionSet": {"id": "example-zh-cn-v1", "fingerprint": "synthetic-demo"},
        "providerCount": 6,
        "recordCount": len(records),
        "providers": PROVIDERS,
        "records": records,
        "trend": [{"date": "2026-01-01", "providerCount": 6, "runCount": 6, "answerCount": 30, "availableCount": 30, "unavailableCount": 0, "mentionRate": 40.0, "chineseMentionRate": 40.0, "englishMentionRate": 0.0, "averageRank": 3.0, "averageScore": round(sum(scores) / len(scores), 2)}],
        "modelTrend": {provider["id"]: [{"date": "2026-01-01", "providerCount": 1, "runCount": 1, "answerCount": 5, "availableCount": 5, "unavailableCount": 0, "mentionRate": 40.0, "chineseMentionRate": 40.0, "englishMentionRate": 0.0, "averageRank": index % 3 + 2, "averageScore": round(sum(record["metrics"]["visibility_score"] for record in records if record["modelProvider"] == provider["id"]) / 5, 2)}] for index, provider in enumerate(PROVIDERS)},
        "batchHistory": [{"runId": f"demo-{provider['id']}", "runAt": "2026-01-01T09:00:00+08:00", "runDate": "2026-01-01", "provider": provider["id"], "modelLabel": provider["label"], "status": "complete", "availableCount": 5, "promptCount": 5, "mentionRate": 40.0, "averageRank": index % 3 + 2, "averageScore": round(sum(record["metrics"]["visibility_score"] for record in records if record["modelProvider"] == provider["id"]) / 5, 2), "questionSetId": "example-zh-cn-v1"} for index, provider in enumerate(PROVIDERS)],
        "monitoringPlan": {"enabled": False, "cadence": "weekly", "time": "09:00", "timezone": "Asia/Shanghai", "weekday": 0, "providers": [provider["id"] for provider in PROVIDERS], "questionSetId": "example-zh-cn-v1", "schedulerStatus": "not_installed"},
    }
    OUTPUT.write_text("window.GEO_ANSWER_DATA=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
