# Security Policy

## Supported version

The latest release on the default branch receives security fixes.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting for the repository. Do not open a public issue containing secrets, customer data or a working exploit. If private reporting has not yet been enabled, contact the repository owner privately.

## Deployment boundary

- The dashboard server is intended for `127.0.0.1` / `localhost` only.
- Do not expose it directly to the public internet. Put authentication and TLS in front of it if you deliberately deploy it remotely.
- The server rejects non-loopback clients, untrusted `Host` headers and cross-origin configuration writes.
- API keys must stay in environment variables or the macOS Keychain. They must never be committed to `config.json`, reports or browser data.
- Run data can contain model answers and citation URLs. Treat it as potentially sensitive and review it before sharing.
