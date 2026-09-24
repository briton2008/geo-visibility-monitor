# Changelog

All notable changes to GEO Visibility Lab are documented here.

## [0.1.1] - 2026-09-24

### Changed

- Renamed the project from **GEO Visibility Monitor** to **GEO Visibility Lab** to distinguish it from similarly named repositories while preserving the established GEO visibility positioning.
- Renamed the repository, plugin, skill, Python package and cover asset to `geo-visibility-lab`.
- Updated the illustrated cover, social metadata, GitHub Pages URLs, installation commands and agent integration metadata for the new identity.

### Added

- GitHub issue forms, pull request template and Contributor Covenant code of conduct.
- Migration notes for existing users of the former repository and plugin name.

## [0.1.0] - 2026-09-22

### Added

- Self-hosted bilingual dashboard for brand mentions, explicit rankings, citations, failure states and comparable trends.
- Versioned question sets, Chinese and English alias tracking, per-answer evidence inspection and transparent scoring.
- Daily, weekly and manual monitoring plans without silently installing a system scheduler.
- Provider guidance for Alibaba Cloud Model Studio, Volcengine Ark, DeepSeek, Gemini, OpenAI and compatible endpoints.
- Deterministic synthetic demo data, GitHub Pages demo, desktop screenshots and an illustrated project cover.
- Claude Code, Codex, Gemini CLI and `AGENTS.md` integration metadata.
- Apache-2.0 license, contribution guide, security policy, trademark notice and third-party notices.

### Changed

- Dashboard overview values now come from the active dataset rather than hard-coded demo metrics.
- Local production datasets can supply their own brand profile while the public demo remains fictional.
- Kimi guidance now uses the non-reasoning `kimi-k2.6` model with `enable_thinking=false` instead of reasoning-only Kimi-K3.
- English UI translation now covers dynamic monitoring and local-production states.

### Fixed

- The local dashboard server now serves the illustrated project cover.
- Release checks inspect Git-tracked release files while keeping ignored private runtime data outside the public package.
- Tests use the public example configuration and no longer depend on a user's private local `config.json`.

[0.1.1]: https://github.com/briton2008/geo-visibility-lab/releases/tag/v0.1.1
[0.1.0]: https://github.com/briton2008/geo-visibility-lab/releases/tag/v0.1.0
