"""Python API — CLI is a consumer of this."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from devforge.core.context import ProjectContext
from devforge.core.generator import GenerationResult, Generator
from devforge.core.registry import ProviderRegistry
from devforge.core.resolver import DependencyResolver
from devforge.core.validator import Validator
from devforge.providers.discovery import create_registry


class ProjectBuilder:
    """Programmatic API: configure() then generate()."""

    def __init__(self, registry: ProviderRegistry | None = None) -> None:
        self.registry = registry or create_registry()
        self.generator = Generator(self.registry)
        self.resolver = DependencyResolver(self.registry)
        self.validator = Validator(self.registry)
        self._data: dict[str, Any] = {}

    def configure(self, **kwargs: Any) -> ProjectContext:
        self._data.update(kwargs)
        ctx = ProjectContext(**self._data)
        resolution = self.resolver.resolve(ctx)
        # apply safe auto-adds
        ctx = resolution.context
        self._data = ctx.model_dump()
        self.validator.ensure_valid(ctx)
        return ctx

    @property
    def context(self) -> ProjectContext:
        return ProjectContext(**self._data)

    def dry_run(self) -> dict:
        ctx = self.context
        plan = self.generator.plan(ctx)
        return {
            "files": sorted(plan.files.keys()),
            "packages": plan.packages,
            "env_keys": sorted(plan.env.keys()),
        }

    def generate(
        self, output_dir: str | Path = ".", *, overwrite: bool = False, install: bool = False
    ) -> GenerationResult:
        ctx = self.context
        return self.generator.generate(ctx, Path(output_dir), overwrite=overwrite, install=install)
