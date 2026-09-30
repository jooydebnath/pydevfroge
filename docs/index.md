# DevForge docs

- Quick start: `pip install devforge && devforge`
- Interactive wizard asks only relevant questions (Celery -> broker, Docker -> services derived).
- Supported providers: `devforge info`
- Architecture: provider registry + composable generator (no template explosion).
- Plugin development: implement `devforge.Provider`, expose via `devforge.providers` entry point.
- Manifest: `.devforge/project.yaml` describes every generated project.
- Commands: `devforge`, `devforge create`, `devforge doctor`, `devforge info`.
- Troubleshooting: run with `--verbose`; use `--dry-run` to preview.
