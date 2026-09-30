"""Provider interface — designed for long-term backward compatibility."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from devforge.core.context import ProjectContext


@dataclass(frozen=True)
class ProviderMetadata:
    """Structured, validated provider metadata."""

    name: str
    display_name: str
    category: str
    packages: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "category": self.category,
            "packages": list(self.packages),
            "requires": list(self.requires),
            "conflicts": list(self.conflicts),
            "capabilities": list(self.capabilities),
        }


@dataclass
class QuestionSpec:
    """A wizard question contributed by a provider.

    ``key`` is stored on ``ProjectContext`` (core field if it matches,
    otherwise ``extras[key]``). ``options`` empty means free text.
    """

    key: str
    prompt: str
    options: list[str] = field(default_factory=list)
    default: Any = None
    kind: str = "select"  # select | confirm | text
    condition: Any = None  # optional callable(context) -> bool
    help: str = ""


class Provider:  # ABC not required; hooks all have defaults for plugin compat
    """Base class every provider (built-in or third-party) extends."""

    name: str = "base"
    display_name: str = "Base"
    category: str = "base"
    version: str = "1.0.0"
    description: str = ""
    packages: list[str] = []
    requires: list[str] = []
    conflicts: list[str] = []
    capabilities: list[str] = []

    @property
    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            name=self.name,
            display_name=self.display_name,
            category=self.category,
            packages=list(self.packages),
            requires=list(self.requires),
            conflicts=list(self.conflicts),
            capabilities=list(self.capabilities),
            description=self.description,
        )

    # -- hooks (all optional with sane defaults) --

    def supports(self, context: ProjectContext) -> bool:  # noqa: ARG002
        return True

    def validate(self, context: ProjectContext) -> list[str]:  # noqa: ARG002
        return []

    def dependencies(self, context: ProjectContext) -> list[str]:  # noqa: ARG002
        """Provider names (not pip packages) this provider needs."""
        return list(self.requires)

    def packages_for(self, context: ProjectContext) -> list[str]:  # noqa: ARG002
        return list(self.packages)

    def environment(self, context: ProjectContext) -> dict[str, str]:  # noqa: ARG002
        return {}

    def questions(self, context: ProjectContext) -> list[QuestionSpec]:  # noqa: ARG002
        return []

    def generate(
        self, context: ProjectContext, project_dir: Path, files: dict[str, str]
    ) -> dict[str, str]:
        """Contribute files. Return updated files dict (may mutate)."""
        return files

    def docker_service(self, context: ProjectContext) -> dict[str, Any] | None:  # noqa: ARG002
        return None

    def dockerfile_snippet(self, context: ProjectContext) -> str | None:  # noqa: ARG002
        return None

    def post_generate(self, context: ProjectContext, project_dir: Path) -> list[str]:
        return []
