import unittest
from unittest import mock
import socket
import copy
import datetime as dt
from zoneinfo import ZoneInfo

import domestic_geo as geo
import build_web_data
import dashboard_server
import monitoring_runner


class DomesticGeoTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "brand": {
                "name": "示例天然食品有限公司",
                "aliases": ["示例品牌", "Example Naturals"],
                "official_domains": ["example.com"],
            },
            "scoring": {
                "name": "transparent_replica_v1",
                "rank_weight": 0.7,
                "citation_weight": 0.2,
                "official_source_weight": 0.1,
            },
        }

    def test_normalize_search_response(self):
        raw = {
            "Response": {
                "Pages": [
                    '{"title":"示例品牌","url":"https://example.com/zh/","passage":"<b>示例产品</b>","score":0.9}'
                ]
            }
        }
        result = geo.normalize_search_response(raw)
        self.assertEqual(result[0]["id"], "S1")
        self.assertEqual(result[0]["passage"], "示例产品")

    def test_score_answer(self):
        results = [
            {"id": "S1", "url": "https://heng-li-yuan.com/zh/"},
            {"id": "S2", "url": "https://example.com/a"},
        ]
        answer = {
            "answer_markdown": "1. 示例品牌 [S1] [S2]",
            "recommended_entities": [{"name": "示例品牌", "rank": 1, "evidence_ids": ["S1", "S2"]}],
            "citations_used": ["S1", "S2", "S99"],
        }
        scored = geo.score_answer(self.config, answer, results)
        self.assertTrue(scored["brand_mentioned"])
        self.assertEqual(scored["brand_rank"], 1)
        self.assertTrue(scored["official_domain_cited"])
        self.assertEqual(scored["citations_used"], ["S1", "S2"])
        self.assertEqual(scored["visibility_score"], 88.0)
        self.assertEqual(scored["identity_match_status"], "supported")
        self.assertIn("official_domain_cited", scored["identity_evidence"])
        self.assertEqual(scored["matched_aliases"], ["示例品牌"])
        self.assertEqual(scored["alias_mention_counts"], {"示例品牌": 1})
        self.assertTrue(scored["mention_snippets"])

    def test_all_customer_aliases_are_counted_and_visible(self):
        details = geo.brand_match_details(
            self.config,
            "示例品牌是候选供应商，英文资料使用 Example Naturals，后文再次写示例品牌。",
        )
        self.assertEqual(details["matched_aliases"], ["示例品牌", "Example Naturals"])
        self.assertEqual(details["matched_chinese_aliases"], ["示例品牌"])
        self.assertEqual(details["matched_english_aliases"], ["Example Naturals"])
        self.assertTrue(details["chinese_name_mentioned"])
        self.assertTrue(details["english_name_mentioned"])
        self.assertEqual(details["alias_mention_counts"], {"示例品牌": 2, "Example Naturals": 1})
        self.assertEqual(details["mention_count"], 3)

    def test_latin_alias_does_not_match_inside_another_word(self):
        config = copy.deepcopy(self.config)
        config["brand"]["aliases"].append("HLY")
        details = geo.brand_match_details(config, "This is highly relevant, but no standalone abbreviation.")
        self.assertFalse(details["mentioned"])

    def test_negative_brand_context_is_flagged_but_still_counted(self):
        details = geo.brand_match_details(self.config, "本轮没有提到示例品牌。")
        self.assertTrue(details["mentioned"])
        self.assertTrue(details["negative_only"])
        self.assertEqual(details["negative_context"][0]["alias"], "示例品牌")

    def test_unavailable_is_not_zero(self):
        records = [{"prompt": "x", "status": "unavailable", "error": "no key"}]
        summary = geo.build_summary(records, "transparent_replica_v1")
        self.assertIsNone(summary["mention_rate_percent"])
        self.assertIsNone(summary["average_visibility_score"])

    def test_citation_metadata_does_not_cache_passage(self):
        results = [{"id": "S1", "position": 1, "title": "x", "url": "https://example.com", "passage": "provider text"}]
        metadata = geo.citation_metadata(results)
        self.assertNotIn("passage", metadata[0])
        self.assertEqual(metadata[0]["url"], "https://example.com")

    def test_provider_error_is_exposed(self):
        with self.assertRaisesRegex(geo.GeoError, "UnauthorizedOperation"):
            geo.normalize_search_response(
                {"Response": {"Error": {"Code": "UnauthorizedOperation", "Message": "未授权操作。"}}}
            )

    def test_provider_config_selects_requested_model(self):
        config = {
            "default_model_provider": "deepseek",
            "models": {
                "deepseek": {"name": "deepseek-flash"},
                "bailian-qwen": {"name": "qwen3.8-flash"},
            },
        }
        selected = geo.provider_config(config, "bailian-qwen")
        self.assertEqual(selected["id"], "bailian-qwen")
        self.assertEqual(selected["name"], "qwen3.8-flash")

    def test_provider_config_rejects_unknown_provider(self):
        config = {"default_model_provider": "deepseek", "models": {"deepseek": {"name": "x"}}}
        with self.assertRaisesRegex(geo.GeoError, "未知模型供应商"):
            geo.provider_config(config, "missing")

    def test_post_json_turns_socket_timeout_into_geo_error(self):
        with mock.patch("urllib.request.urlopen", side_effect=socket.timeout("timed out")):
            with self.assertRaisesRegex(geo.GeoError, "网络请求超时"):
                geo.post_json("https://example.com", {}, {}, 1)

    def test_active_question_set_is_versioned_and_fingerprinted(self):
        config = {
            "question_sets": {
                "active_version": "brand-zh-v1",
                "versions": [
                    {
                        "id": "brand-zh-v1",
                        "language": "zh-CN",
                        "market": "CN",
                        "questions": [
                            {
                                "id": "brand-facts-001",
                                "track": "benchmark",
                                "intent": "brand_knowledge",
                                "text": "这个品牌提供什么？",
                                "tags": ["品牌认知"],
                                "enabled": True,
                            }
                        ],
                    }
                ],
            }
        }
        question_set = geo.active_question_set(config)
        self.assertEqual(question_set["id"], "brand-zh-v1")
        self.assertEqual(len(question_set["fingerprint"]), 64)
        self.assertEqual(geo.active_questions(question_set)[0]["id"], "brand-facts-001")

    def test_question_edit_changes_fingerprint(self):
        question_set = {
            "id": "brand-zh-v1",
            "language": "zh-CN",
            "market": "CN",
            "questions": [
                {
                    "id": "q-001",
                    "track": "benchmark",
                    "intent": "brand_knowledge",
                    "text": "问题A",
                    "tags": [],
                    "enabled": True,
                }
            ],
        }
        changed = copy.deepcopy(question_set)
        changed["questions"][0]["text"] = "问题B"
        self.assertNotEqual(
            geo.question_set_fingerprint(question_set),
            geo.question_set_fingerprint(changed),
        )

    def test_question_set_rejects_duplicate_ids(self):
        question_set = {
            "id": "brand-zh-v1",
            "questions": [
                {"id": "q-001", "track": "benchmark", "text": "问题A"},
                {"id": "q-001", "track": "discovery", "text": "问题B"},
            ],
        }
        with self.assertRaisesRegex(geo.GeoError, "问题ID重复"):
            geo.validate_question_set(question_set)

    def test_legacy_prompts_remain_readable_but_are_unversioned(self):
        question_set = geo.active_question_set({"prompts": ["旧问题"]})
        self.assertEqual(question_set["id"], "legacy-unversioned")
        self.assertEqual(question_set["questions"][0]["track"], "benchmark")

    def test_run_settings_snapshot_excludes_secrets(self):
        config = {"search": {"mode": 0, "results_per_prompt": 10, "timeout_seconds": 45}}
        model = {
            "id": "provider-a",
            "name": "model-a",
            "temperature": 0,
            "max_tokens": 1000,
            "timeout_seconds": 60,
            "env_key": "SECRET_ENV",
            "keychain_service": "secret-service",
            "extra_payload": {"thinking": {"type": "disabled"}},
        }
        snapshot = geo.run_settings_snapshot(config, model)
        self.assertEqual(snapshot["model_name"], "model-a")
        self.assertEqual(snapshot["thinking"], {"type": "disabled"})
        self.assertNotIn("env_key", snapshot)
        self.assertNotIn("keychain_service", snapshot)

    def test_brand_profile_snapshot_keeps_customer_context_separate(self):
        config = copy.deepcopy(self.config)
        config["brand"].update(
            {
                "business_description": "天然甜味剂供应商",
                "core_offerings": ["罗汉果提取物", "复配甜味剂"],
                "primary_markets": ["中国", "海外"],
            }
        )
        profile = geo.brand_profile_snapshot(config)
        self.assertEqual(profile["business_description"], "天然甜味剂供应商")
        self.assertEqual(profile["core_offerings"], ["罗汉果提取物", "复配甜味剂"])
        self.assertNotIn("models", profile)

    def test_alias_only_identity_is_flagged_without_changing_mention(self):
        answer = {
            "answer_markdown": "示例品牌进入候选名单。",
            "recommended_entities": [],
            "citations_used": [],
        }
        scored = geo.score_answer(self.config, answer, [])
        self.assertTrue(scored["brand_mentioned"])
        self.assertEqual(scored["identity_match_status"], "alias_only")

    def test_business_terms_do_not_create_identity_evidence_without_brand(self):
        config = copy.deepcopy(self.config)
        config["brand"]["core_offerings"] = ["罗汉果提取物"]
        answer = {"answer_markdown": "可采购罗汉果提取物。", "recommended_entities": [], "citations_used": []}
        scored = geo.score_answer(config, answer, [])
        self.assertFalse(scored["brand_mentioned"])
        self.assertEqual(scored["identity_match_status"], "not_applicable")
        self.assertEqual(scored["identity_evidence"], [])

    def test_usage_metadata_keeps_only_numeric_token_counts(self):
        raw = {
            "usage": {
                "prompt_tokens": 12,
                "completion_tokens": 8,
                "total_tokens": 20,
                "billing_detail": "private",
            }
        }
        self.assertEqual(
            geo.usage_metadata(raw),
            {"prompt_tokens": 12, "completion_tokens": 8, "total_tokens": 20},
        )

    def test_error_states_are_distinct(self):
        self.assertEqual(geo.classify_error("网络请求超时: 30 秒"), "timeout")
        self.assertEqual(geo.classify_error("HTTP 429: Too Many Requests"), "rate_limited")
        self.assertEqual(geo.classify_error("模型未返回约定的结构化 JSON"), "parse_error")
        self.assertEqual(geo.classify_error("HTTP 401: Unauthorized"), "api_error")

    def test_summary_keeps_failure_states_out_of_mention_denominator(self):
        records = [
            {
                "prompt": "a",
                "status": "ok",
                "result_state": "mentioned",
                "metrics": {
                    "brand_mentioned": True,
                    "brand_rank": 2,
                    "visibility_score": 50,
                    "citation_domains": [],
                },
            },
            {
                "prompt": "b",
                "status": "ok",
                "result_state": "not_mentioned",
                "metrics": {
                    "brand_mentioned": False,
                    "brand_rank": None,
                    "visibility_score": 0,
                    "citation_domains": [],
                },
            },
            {"prompt": "c", "status": "unavailable", "result_state": "timeout"},
        ]
        summary = geo.build_summary(records, "transparent_replica_v1")
        self.assertEqual(summary["mention_rate_percent"], 50.0)
        self.assertEqual(summary["chinese_name_mention_rate_percent"], 0.0)
        self.assertEqual(summary["english_name_mention_rate_percent"], 0.0)
        self.assertEqual(summary["available_count"], 2)
        self.assertEqual(summary["unavailable_count"], 1)
        self.assertEqual(
            summary["result_state_counts"],
            {"mentioned": 1, "not_mentioned": 1, "timeout": 1},
        )

    def test_summary_separates_chinese_and_english_name_rates(self):
        records = [
            {
                "status": "ok",
                "metrics": {
                    "brand_mentioned": True,
                    "chinese_name_mentioned": True,
                    "english_name_mentioned": False,
                    "brand_rank": 1,
                    "visibility_score": 80,
                    "citation_domains": [],
                },
            },
            {
                "status": "ok",
                "metrics": {
                    "brand_mentioned": True,
                    "chinese_name_mentioned": False,
                    "english_name_mentioned": True,
                    "brand_rank": 2,
                    "visibility_score": 70,
                    "citation_domains": [],
                },
            },
        ]
        summary = geo.build_summary(records, "transparent_replica_v1")
        self.assertEqual(summary["mention_rate_percent"], 100.0)
        self.assertEqual(summary["chinese_name_mention_rate_percent"], 50.0)
        self.assertEqual(summary["english_name_mention_rate_percent"], 50.0)

    def test_monitoring_plan_counts_calls_without_executing(self):
        config = geo.read_json(geo.ROOT / "config.example.json")
        plan = monitoring_runner.monitoring_plan(config)
        self.assertFalse(plan["enabled"])
        self.assertEqual(plan["question_count"], 5)
        self.assertEqual(len(plan["providers"]), 6)
        self.assertEqual(plan["planned_model_calls"], 30)
        self.assertEqual(plan["planned_search_calls"], 30)

    def test_disabled_monitoring_plan_is_never_due(self):
        plan = {
            "enabled": False,
            "time": "09:00",
            "timezone": "Asia/Shanghai",
        }
        now = dt.datetime(2026, 9, 21, 10, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
        self.assertFalse(monitoring_runner.is_due(plan, {}, now))

    def test_enabled_monitoring_runs_once_per_local_day(self):
        plan = {
            "enabled": True,
            "time": "09:00",
            "timezone": "Asia/Shanghai",
        }
        now = dt.datetime(2026, 9, 21, 10, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
        self.assertTrue(monitoring_runner.is_due(plan, {}, now))
        self.assertFalse(monitoring_runner.is_due(plan, {"last_completed_date": "2026-09-21"}, now))

    def test_weekly_monitoring_only_runs_on_selected_weekday(self):
        plan = {
            "enabled": True,
            "cadence": "weekly",
            "weekday": 0,
            "time": "09:00",
            "timezone": "Asia/Shanghai",
        }
        monday = dt.datetime(2026, 9, 21, 10, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
        tuesday = monday + dt.timedelta(days=1)
        self.assertTrue(monitoring_runner.is_due(plan, {}, monday))
        self.assertFalse(monitoring_runner.is_due(plan, {}, tuesday))

    def test_manual_monitoring_is_never_due(self):
        plan = {
            "enabled": True,
            "cadence": "manual",
            "weekday": 0,
            "time": "09:00",
            "timezone": "Asia/Shanghai",
        }
        now = dt.datetime(2026, 9, 21, 10, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
        self.assertFalse(monitoring_runner.is_due(plan, {}, now))

    def test_monitoring_api_validation_preserves_only_allowed_fields(self):
        config = geo.read_json(geo.ROOT / "config.example.json")
        payload = {
            "enabled": True,
            "cadence": "weekly",
            "time": "08:30",
            "weekday": 2,
            "providers": ["provider-a"],
            "secret": "must-not-be-saved",
        }
        validated = dashboard_server.validate_monitoring_payload(payload, config)
        self.assertEqual(validated["cadence"], "weekly")
        self.assertEqual(validated["weekday"], 2)
        self.assertEqual(validated["providers"], ["provider-a"])
        self.assertNotIn("secret", validated)

    def test_dashboard_rejects_non_loopback_host_headers(self):
        self.assertTrue(dashboard_server.is_loopback_host("127.0.0.1:4187"))
        self.assertTrue(dashboard_server.is_loopback_host("localhost:4187"))
        self.assertFalse(dashboard_server.is_loopback_host("attacker.invalid"))

    def test_dashboard_rejects_cross_origin_posts(self):
        self.assertTrue(dashboard_server.is_allowed_origin("http://127.0.0.1:4187"))
        self.assertTrue(dashboard_server.is_allowed_origin("http://localhost:4187"))
        self.assertFalse(dashboard_server.is_allowed_origin("https://attacker.invalid"))

    def test_legacy_run_is_comparable_only_when_prompts_match(self):
        active = {
            "id": "brand-zh-v1",
            "fingerprint": "abc",
            "questions": [{"id": "q1", "track": "benchmark", "text": "问题A", "enabled": True}],
        }
        matching = {"records": [{"prompt": "问题A"}]}
        changed = {"records": [{"prompt": "问题B"}]}
        self.assertTrue(build_web_data.question_set_compatible(matching, active))
        self.assertFalse(build_web_data.question_set_compatible(changed, active))


if __name__ == "__main__":
    unittest.main()
