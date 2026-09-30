"""Dependency model used by the resolver."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DependencyRequirement:
    provider: str
    reason: str = ""
    optional: bool = False
    choices: list[str] = field(default_factory=list)
