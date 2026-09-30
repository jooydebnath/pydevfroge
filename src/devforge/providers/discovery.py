"""Plugin discovery via entry points + builtin registration."""

from __future__ import annotations

from importlib.metadata import entry_points

from devforge.core.registry import ProviderRegistry


def discover_external_providers(
    registry: ProviderRegistry, group: str = "devforge.providers"
) -> int:
    """Load third-party providers without touching core. Returns count loaded."""
    count = 0
    try:
        eps = entry_points(group=group)
    except TypeError:  # older Python
        eps = entry_points().get(group, [])
    for ep in eps:
        try:
            factory = ep.load()
            provider = factory() if callable(factory) else factory
            if not registry.has(provider.name):
                registry.register(provider)
                count += 1
        except Exception:
            continue
    return count


def create_registry(*, load_plugins: bool = True) -> ProviderRegistry:
    """Build registry with all built-in providers."""
    from devforge.providers.builtin.authentication.providers import (
        JWTProvider,
        NoneAuthProvider,
        OAuth2Provider,
        SessionAuthProvider,
    )
    from devforge.providers.builtin.databases.providers import (
        MySQLProvider,
        NoneDatabaseProvider,
        PostgreSQLProvider,
        SQLiteProvider,
    )
    from devforge.providers.builtin.frameworks.providers import (
        DjangoProvider,
        FastAPIProvider,
        FlaskProvider,
        NoneFrameworkProvider,
    )
    from devforge.providers.builtin.infrastructure.providers import (
        DockerProvider,
        GitHubActionsProvider,
        NginxProvider,
        NoneCICDProvider,
    )
    from devforge.providers.builtin.services.providers import (
        CeleryProvider,
        NoneCacheProvider,
        NoneQueueProvider,
        RabbitMQProvider,
        RedisProvider,
        RQProvider,
    )
    from devforge.providers.builtin.testing.providers import (
        NoneTestingProvider,
        PytestProvider,
        UnittestProvider,
    )
    from devforge.providers.builtin.tooling.providers import (
        GitProvider,
        PreCommitProvider,
        RuffProvider,
    )

    registry = ProviderRegistry()
    for cls in (
        DjangoProvider,
        FastAPIProvider,
        FlaskProvider,
        NoneFrameworkProvider,
        PostgreSQLProvider,
        MySQLProvider,
        SQLiteProvider,
        NoneDatabaseProvider,
        JWTProvider,
        SessionAuthProvider,
        OAuth2Provider,
        NoneAuthProvider,
        RedisProvider,
        NoneCacheProvider,
        CeleryProvider,
        RQProvider,
        NoneQueueProvider,
        RabbitMQProvider,
        PytestProvider,
        UnittestProvider,
        NoneTestingProvider,
        RuffProvider,
        PreCommitProvider,
        GitProvider,
        DockerProvider,
        GitHubActionsProvider,
        NoneCICDProvider,
        NginxProvider,
    ):
        registry.register(cls())
    if load_plugins:
        discover_external_providers(registry)
    return registry
