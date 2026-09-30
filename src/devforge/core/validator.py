"""Validation / conflict engine — never silently emits invalid projects."""

from __future__ import annotations

from devforge.core.context import ProjectContext
from devforge.core.exceptions import ConflictError, ValidationError
from devforge.core.registry import ProviderRegistry


class Validator:
    def __init__(self, registry: ProviderRegistry) -> None:
        self.registry = registry

    def validate(self, context: ProjectContext) -> list[str]:
        """Return list of error strings (empty = valid)."""
        errors: list[str] = []

        # unknown provider names
        for attr in ("framework", "database", "authentication", "cache", "task_queue", "testing"):
            val = getattr(context, attr)
            if val not in ("none", "", None) and not self.registry.has(val):
                errors.append(f"Unknown provider '{val}' for {attr}.")

        if context.broker not in ("none", "", None) and not self.registry.has(context.broker):
            errors.append(f"Unknown broker provider '{context.broker}'.")
        if context.cicd not in ("none", "", None) and not self.registry.has(context.cicd):
            errors.append(f"Unknown CI/CD provider '{context.cicd}'.")
        if context.framework not in ("none", "", None) and not self.registry.has(context.framework):
            errors.append(f"Unknown framework '{context.framework}'.")

        # celery without broker
        if (
            context.task_queue == "celery"
            and context.broker
            in (
                "none",
                "",
                None,
            )
            and context.cache not in ("redis", "rabbitmq")
        ):
            errors.append("Celery requires a broker (Redis or RabbitMQ).")

        # delegate to providers
        for provider in self.registry.active_for(context):
            try:
                for err in provider.validate(context):
                    errors.append(err)
            except Exception as exc:  # keep validator robust
                errors.append(f"Provider '{provider.name}' validation crashed: {exc}")

        # conflict metadata check
        active_names = {p.name for p in self.registry.active_for(context)}
        for provider in self.registry.active_for(context):
            for conflict in provider.conflicts:
                if conflict in active_names:
                    errors.append(f"Provider '{provider.name}' conflicts with '{conflict}'.")

        return errors

    def ensure_valid(self, context: ProjectContext) -> None:
        errors = self.validate(context)
        if errors:
            # single conflict error carrying details
            raise ValidationError("; ".join(errors))

    def ensure_no_conflict(self, context: ProjectContext) -> None:
        errors = self.validate(context)
        conflicts = [e for e in errors if "conflict" in e.lower()]
        if conflicts:
            raise ConflictError("; ".join(conflicts))
