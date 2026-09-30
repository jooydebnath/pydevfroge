"""Unit tests for registry / resolver / validator."""

from devforge.core.context import ProjectContext
from devforge.core.validator import Validator
from devforge.providers.discovery import create_registry


def _registry():
    return create_registry(load_plugins=False)


def test_registry_has_builtin():
    reg = _registry()
    assert reg.has("django")
    assert reg.has("fastapi")
    assert reg.has("postgresql")
    assert reg.has("redis")
    assert reg.has("celery")
    assert reg.has("docker")


def test_active_for_no_if_chain():
    reg = _registry()
    ctx = ProjectContext(name="x", framework="django", database="postgresql")
    active = {p.name for p in reg.active_for(ctx)}
    assert "django" in active
    assert "postgresql" in active


def test_resolver_celery_needs_broker():
    reg = _registry()
    from devforge.core.resolver import DependencyResolver

    r = DependencyResolver(reg)
    ctx = ProjectContext(name="x", framework="django", task_queue="celery")
    res = r.resolve(ctx)
    assert any(c["key"] == "broker" for c in res.needed_choices)


def test_resolver_redis_satisfies_broker():
    reg = _registry()
    from devforge.core.resolver import DependencyResolver

    r = DependencyResolver(reg)
    ctx = ProjectContext(name="x", task_queue="celery", cache="redis")
    res = r.resolve(ctx)
    assert res.context.broker == "redis"


def test_validator_rejects_celery_without_broker():
    reg = _registry()
    v = Validator(reg)
    ctx = ProjectContext(name="x", task_queue="celery")
    assert v.validate(ctx)


def test_pip_packages_postgres_driver_auto():
    reg = _registry()
    from devforge.core.resolver import DependencyResolver

    r = DependencyResolver(reg)
    ctx = ProjectContext(name="x", framework="django", database="postgresql")
    pkgs = r.pip_packages(ctx)
    assert any("psycopg" in p for p in pkgs)
    assert any("django" in p.lower() for p in pkgs)
