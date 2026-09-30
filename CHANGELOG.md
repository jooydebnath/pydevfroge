# Changelog

## 0.5.0 — MVP

- Core engine: ProjectContext, registry, resolver, validator, generator
- Dynamic provider-contributed wizard
- Providers: Django, FastAPI, Flask, PostgreSQL, MySQL, SQLite, Redis,
  RabbitMQ, Celery, RQ, JWT, Session, OAuth2, pytest, unittest, Ruff,
  pre-commit, Git, Docker, GitHub Actions, Nginx
- Commands: `devforge`, `devforge create`, `devforge doctor`, `devforge info`
- `--dry-run`, `--verbose`, `--overwrite`
- `.devforge/project.yaml` manifest
- Python API: `ProjectBuilder`
- Entry-point plugin discovery (`devforge.providers`)
