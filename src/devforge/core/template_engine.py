"""Jinja2 template engine wrapper."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import BaseLoader, Environment, StrictUndefined


class TemplateEngine:
    def __init__(self, template_dirs: list[Path] | None = None) -> None:
        self.env = Environment(
            loader=BaseLoader(),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        )
        self.template_dirs = template_dirs or []

    def render_string(self, template: str, variables: dict[str, Any]) -> str:
        return self.env.from_string(template).render(**variables)

    def render_file(self, path: Path, variables: dict[str, Any]) -> str:
        return self.render_string(path.read_text(encoding="utf-8"), variables)

    def find(self, name: str) -> Path | None:
        for d in self.template_dirs:
            candidate = d / name
            if candidate.exists():
                return candidate
        return None
