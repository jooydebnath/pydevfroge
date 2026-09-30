"""Unit tests for ProjectContext."""

from devforge.core.context import ProjectContext


def test_package_name():
    ctx = ProjectContext(name="ecommerce-api")
    assert ctx.package_name == "ecommerce_api"
    assert ctx.slug == "ecommerce-api"


def test_selected_providers():
    ctx = ProjectContext(name="x", framework="django", database="postgresql", docker=True)
    sel = ctx.selected_providers()
    assert sel["framework"] == "django"
    assert sel["container"] == "docker"
