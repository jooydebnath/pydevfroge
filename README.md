# DevForge — Dynamic Python Project Bootstrap & Automation

```bash
pip install devforge
devforge
```

DevForge is a **provider-based, composable project generator**. No fixed
templates, no giant `if/elif` chains — every technology is a provider that
contributes packages, environment, files, Docker services and wizard questions.

## Quick start

```bash
pip install devforge
devforge --help
devforge create --help

# Non-interactive example
devforge create --name my-api --framework fastapi --database postgresql \
  --docker --cicd github-actions --output ./out --overwrite

# Preview without writing
devforge create --name demo --framework django --database postgresql --dry-run

# Programmatic API
python -c "
from devforge import ProjectBuilder
b = ProjectBuilder()
b.configure(name='my-api', framework='fastapi', database='postgresql', docker=True)
print(b.dry_run())
b.generate('./out', overwrite=True)
"
```

## Architecture

```
Core Engine -> Provider Registry -> Providers -> Generator -> Ready Project
```

See `docs/` for installation, wizard, providers, plugin development, manifest,
commands and troubleshooting.

## Plugin development

```python
from devforge import Provider

class MongoProvider(Provider):
    name = "mongodb"
    display_name = "MongoDB"
    category = "database"
    packages = ["pymongo>=4.0"]
```

Register via entry point group `devforge.providers` — no core edits needed.

## License

MIT — see LICENSE.
