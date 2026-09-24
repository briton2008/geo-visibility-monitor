# Contributing

感谢参与 GEO Visibility Lab。Please keep contributions small, testable and evidence-bounded.

## Development

```bash
python3 scripts/generate_demo_data.py
python3 scripts/bootstrap.py
python3 -m unittest discover -s tests -v
python3 scripts/release_check.py
```

## Pull requests

- Do not commit API keys, `config.json`, real customer runs, private citations or generated `web/answer-data.js`.
- Use fictional `example.com` data in tests and screenshots.
- Preserve `unavailable`, timeout and partial states; do not convert missing data to zero.
- Add tests for scoring, question-set compatibility, persistence or server security changes.
- Keep Chinese and English interface labels aligned when adding user-facing features.

By contributing, you agree that your contribution is licensed under Apache-2.0.
