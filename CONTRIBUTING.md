# Contributing

1. Create a virtualenv, `pip install -e ".[dev]"`.
2. Run `pytest` and `ruff check src tests`.
3. Providers live under `src/devforge/providers/builtin/` — one class per
   technology, no framework `if/elif` in core.
4. Add tests for every new provider.
