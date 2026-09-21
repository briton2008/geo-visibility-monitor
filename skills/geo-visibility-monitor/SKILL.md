---
name: geo-visibility-monitor
description: Configure, run, diagnose, or report the GEO Visibility Monitor in this repository. Use for brand setup, provider connections, scheduled AI-answer monitoring, ranking trends, citation evidence, cost estimates, and evidence-bounded recommendations.
---

# GEO Visibility Monitor

Operate the repository's self-hosted monitor without collapsing distinct evidence layers or hiding failures.

## Route the task

- For brand names, aliases, business context, question sets or cadence, inspect `config.example.json` and the user's local `config.json` if present.
- For model setup, read `../../PROVIDERS.md` and use the provider's current official documentation. Never guess a current model ID or price.
- For collected results, inspect the generated report and raw run records before explaining metrics or recommending action.
- For UI work, preserve the dashboard's dark visual system, bilingual behavior and explicit `unavailable` states.

## Safe operating sequence

1. Read the existing configuration and confirm the active question-set version.
2. Run `python3 domestic_geo.py doctor` before any real collection.
3. Use `python3 monitoring_runner.py` to inspect whether a schedule is due without calling paid APIs.
4. Run `python3 domestic_geo.py run --provider <provider-id>` or `python3 monitoring_runner.py --execute` only when paid execution is already authorized.
5. Run `python3 build_web_data.py`, then open the local dashboard and verify the result.

Do not install a system scheduler automatically. Saving cadence configuration and installing a scheduler are separate states.

## Evidence boundaries

- Mention rate: available answers that contain a configured brand name or alias.
- Average rank: only answers containing an explicit ordered recommendation with a brand position.
- Citation evidence: sources mapped to an answer; a missing mapping is not proof that search had no evidence.
- Search discoverability: what the configured search layer returned at collection time; it is not ordinary-search indexing proof.
- Consumer products: API monitoring is a reproducible benchmark, not an exact replay of an App, website, memory layer or private system prompt.

Keep `timeout`, `rate_limited`, `parse_error`, `api_error` and `unavailable` as distinct states. Unknown values stay `unavailable`; never fill them with zero.

## Security and cost

Read credentials only from environment variables or the supported system keychain. Never display or persist secret values.

Before real execution, report the planned model and search call counts. Treat UI cost output as an estimate; the provider's returned usage and bill are authoritative.
