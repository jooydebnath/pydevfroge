"""DevForge — dynamic Python project bootstrap & automation."""

from devforge.builder import ProjectBuilder
from devforge.core.context import ProjectContext
from devforge.core.registry import ProviderRegistry
from devforge.providers.base import Provider, ProviderMetadata, QuestionSpec
from devforge.providers.discovery import create_registry

__version__ = "0.5.0"

__all__ = [
    "ProjectBuilder",
    "ProjectContext",
    "Provider",
    "ProviderMetadata",
    "ProviderRegistry",
    "QuestionSpec",
    "create_registry",
    "__version__",
]
