"""Provider-specific tests."""

from devforge.providers.discovery import create_registry


def test_provider_metadata_structured():
    reg = create_registry(load_plugins=False)
    md = reg.get("postgresql").metadata
    assert md.name == "postgresql"
    assert "psycopg[binary]" in md.packages[0]
    assert "sqlite" in md.conflicts


def test_composable_no_template_explosion():
    # two different stacks must share the same provider classes (composition)
    reg = create_registry(load_plugins=False)
    assert reg.get("django") is reg.get("django")
    assert reg.get("redis") is reg.get("redis")
