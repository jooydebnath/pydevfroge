"""Testing providers."""

from __future__ import annotations

from devforge.providers.base import Provider


class PytestProvider(Provider):
    name = "pytest"
    display_name = "pytest"
    category = "testing"
    packages = ["pytest>=8.0"]
    capabilities = ["testing"]

    def generate(self, context, project_dir, files):
        if context.testing != "pytest":
            return files
        files["tests/__init__.py"] = ""
        files["tests/test_health.py"] = "def test_health():\n    assert 1 + 1 == 2\n"
        return files


class UnittestProvider(Provider):
    name = "unittest"
    display_name = "unittest"
    category = "testing"
    capabilities = ["testing"]

    def generate(self, context, project_dir, files):
        if context.testing != "unittest":
            return files
        files["tests/__init__.py"] = ""
        files["tests/test_health.py"] = (
            "import unittest\n"
            "class TestHealth(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertEqual(1 + 1, 2)\n"
        )
        return files


class NoneTestingProvider(Provider):
    name = "none-testing"
    display_name = "None"
    category = "testing"
    capabilities = ["testing"]
