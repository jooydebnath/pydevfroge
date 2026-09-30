"""Central ProjectContext — single source of truth for generation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class ProjectContext(BaseModel):
    """Structured, validated project configuration.

    Providers receive this object instead of relying on globals.
    Unknown / provider-specific answers live in ``extras`` so the
    core stays provider-agnostic.
    """

    model_config = {"extra": "forbid", "populate_by_name": True}

    name: str = Field(min_length=1, max_length=100)
    language: str = "python"
    python_version: str = "3.12"

    framework: str = "none"
    database: str = "none"
    authentication: str = "none"
    cache: str = "none"
    task_queue: str = "none"
    broker: str = "none"
    testing: str = "pytest"
    formatter: str = "ruff"
    linter: str = "ruff"
    use_pre_commit: bool = False
    docker: bool = False
    cicd: str = "none"
    web_server: str = "none"
    monitoring: str = "none"
    git: bool = True

    # provider-specific answers, e.g. django_drf=True, celery_beat=True
    extras: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def _validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("project name must not be empty")
        # allow letters, numbers, dash, underscore
        cleaned = v.replace("-", "_").replace(" ", "_")
        if not cleaned.replace("_", "").isalnum():
            raise ValueError("project name may only contain letters, numbers, -, _ and spaces")
        return v

    @property
    def package_name(self) -> str:
        """Safe Python package name derived from project name."""
        return self.name.strip().lower().replace("-", "_").replace(" ", "_")

    @property
    def slug(self) -> str:
        return self.name.strip().lower().replace(" ", "-").replace("_", "-")

    def selected_providers(self) -> dict[str, str]:
        """Map of category -> provider name for non-trivial selections."""
        mapping: dict[str, str] = {}
        if self.framework != "none":
            mapping["framework"] = self.framework
        if self.database != "none":
            mapping["database"] = self.database
        if self.authentication != "none":
            mapping["authentication"] = self.authentication
        if self.cache != "none":
            mapping["cache"] = self.cache
        if self.task_queue != "none":
            mapping["queue"] = self.task_queue
        if self.testing != "none":
            mapping["testing"] = self.testing
        if self.formatter != "none":
            mapping["formatter"] = self.formatter
        if self.docker:
            mapping["container"] = "docker"
        if self.cicd != "none":
            mapping["cicd"] = self.cicd
        if self.web_server != "none":
            mapping["web_server"] = self.web_server
        if self.git:
            mapping["tooling"] = "git"
        return mapping

    def get(self, key: str, default: Any = None) -> Any:
        if key in self.model_fields:
            return getattr(self, key)
        return self.extras.get(key, default)
