# Security

- DevForge generates random `SECRET_KEY` values per project.
- `.env` is git-ignored by default; only `.env.example` (secrets blanked) is safe to commit.
- Secrets are redacted from logs.
- Report vulnerabilities via GitHub Issues.
