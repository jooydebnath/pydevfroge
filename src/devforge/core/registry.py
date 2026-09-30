"""Provider registry — core never hard-codes framework if/elif chains."""

from __future__ import annotations

from devforge.core.exceptions import ProviderError
from devforge.providers.base import Provider


class ProviderRegistry:
    """Holds all providers, queried by category or name."""

    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}  # name -> provider
        self._by_category: dict[str, list[Provider]] = {}

    def register(self, provider: Provider) -> None:
        if provider.name in self._providers:
            raise ProviderError(f"provider '{provider.name}' already registered")
        self._providers[provider.name] = provider
        self._by_category.setdefault(provider.category, []).append(provider)

    def get(self, name: str) -> Provider:
        try:
            return self._providers[name]
        except KeyError:
            raise ProviderError(f"unknown provider '{name}'") from None

    def has(self, name: str) -> bool:
        return name in self._providers

    def options(self, category: str) -> list[Provider]:
        return list(self._by_category.get(category, []))

    def option_names(self, category: str) -> list[str]:
        return [p.name for p in self.options(category)]

    def all(self) -> list[Provider]:
        return list(self._providers.values())

    def active_for(self, context) -> list[Provider]:
        """Providers selected by the given context (no if/elif)."""
        from devforge.core.context import ProjectContext

        assert isinstance(context, ProjectContext)
        wanted: set[str] = set()
        field_to_category = {
            "framework": context.framework,
            "database": context.database,
            "authentication": context.authentication,
            "cache": context.cache,
            "task_queue": context.task_queue,
            "testing": context.testing,
            "formatter": context.formatter,
        }
        for _cat, prov_name in field_to_category.items():
            if prov_name and prov_name != "none" and self.has(prov_name):
                wanted.add(prov_name)
        # broker is a provider too (redis/rabbitmq) but may duplicate cache
        if context.broker not in ("none", "", None) and self.has(context.broker):
            wanted.add(context.broker)
        if context.docker and self.has("docker"):
            wanted.add("docker")
        if context.cicd not in ("none", "", None) and self.has(context.cicd):
            wanted.add(context.cicd)
        if context.web_server not in ("none", "", None) and self.has(context.web_server):
            wanted.add(context.web_server)
        if context.git and self.has("git"):
            wanted.add("git")
        if context.use_pre_commit and self.has("pre-commit"):
            wanted.add("pre-commit")
        # extras-driven providers (e.g. celery beat doesn't add new provider)
        active = [self._providers[n] for n in wanted if n in self._providers]
        # deterministic order by category then name
        active.sort(key=lambda p: (p.category, p.name))
        return active

    def check_duplicates(self) -> None:
        seen_caps: dict[str, str] = {}
        for p in self.all():
            for cap in p.capabilities:
                # capabilities may legitimately repeat across categories;
                # registry just records, validator decides conflicts.
                seen_caps.setdefault(cap, p.name)
