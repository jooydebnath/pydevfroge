"""Dependency resolver — auto-resolves drivers, brokers, auth packages."""

from __future__ import annotations

from dataclasses import dataclass, field

from devforge.core.context import ProjectContext
from devforge.core.registry import ProviderRegistry


@dataclass
class Resolution:
    context: ProjectContext
    auto_added: list[str] = field(default_factory=list)
    needed_choices: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# providers that satisfy the "broker" capability
BROKER_CHOICES = ["redis", "rabbitmq"]
# celery works with redis or rabbitmq
CELERY_BROKERS = ["redis", "rabbitmq"]


class DependencyResolver:
    """Resolves provider-level dependencies without core if/elif per framework."""

    def __init__(self, registry: ProviderRegistry) -> None:
        self.registry = registry

    def resolve(self, context: ProjectContext) -> Resolution:
        auto_added: list[str] = []
        needed_choices: list[dict] = []
        warnings: list[str] = []

        ctx = context.model_copy(deep=True)

        # Celery requires a broker: if task_queue==celery and no broker/cache broker set
        if ctx.task_queue == "celery":
            broker_ok = ctx.broker in CELERY_BROKERS or ctx.cache in CELERY_BROKERS
            if not broker_ok:
                needed_choices.append(
                    {
                        "key": "broker",
                        "prompt": "Celery requires a broker. Select broker",
                        "options": CELERY_BROKERS,
                        "default": "redis",
                    }
                )

        # If user picked redis as cache it doubles as broker — record info
        if ctx.task_queue == "celery" and ctx.cache == "redis" and ctx.broker in ("none", ""):
            ctx.broker = "redis"
            auto_added.append("broker=redis (via cache)")

        # RQ requires redis
        if ctx.task_queue == "rq" and ctx.cache != "redis" and ctx.broker != "redis":
            # auto-add redis as broker/cache
            if ctx.cache == "none":
                ctx.cache = "redis"
                auto_added.append("redis (required by rq)")
            else:
                warnings.append("RQ works best with Redis; continuing without Redis may fail.")

        # Collect pip packages transitively (informational)
        # Provider.requires referencing other providers: ensure they are active
        active = self.registry.active_for(ctx)
        active_names = {p.name for p in active}
        for provider in active:
            for dep in provider.dependencies(ctx):
                if dep not in active_names and self.registry.has(dep):
                    # auto-enable lightweight deps only; brokers need user choice
                    if dep in ("redis", "rabbitmq") and provider.name in ("celery",):
                        continue  # handled via needed_choices
                    warnings.append(f"{provider.name} suggests provider '{dep}'")

        return Resolution(
            context=ctx, auto_added=auto_added, needed_choices=needed_choices, warnings=warnings
        )

    def pip_packages(self, context: ProjectContext) -> list[str]:
        """Union of packages from all active providers, deduped, order-stable."""
        seen: list[str] = []
        for provider in self.registry.active_for(context):
            for pkg in provider.packages_for(context):
                if pkg not in seen:
                    seen.append(pkg)
        return seen
