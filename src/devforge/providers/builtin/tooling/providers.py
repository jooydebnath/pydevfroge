"""Tooling providers: Ruff, pre-commit, Git."""

from __future__ import annotations

from devforge.providers.base import Provider


class RuffProvider(Provider):
    name = "ruff"
    display_name = "Ruff"
    category = "formatter"
    packages = ["ruff>=0.4"]
    capabilities = ["formatter", "linter"]

    def generate(self, context, project_dir, files):
        if context.formatter != "ruff" and context.linter != "ruff":
            return files
        return files  # config lives in pyproject.toml


class PreCommitProvider(Provider):
    name = "pre-commit"
    display_name = "pre-commit"
    category = "formatter"
    packages = ["pre-commit>=3.0"]
    capabilities = ["formatter", "git-hooks"]

    def generate(self, context, project_dir, files):
        if not context.use_pre_commit:
            return files
        files[".pre-commit-config.yaml"] = (
            "repos:\n"
            "  - repo: https://github.com/astral-sh/ruff-pre-commit\n"
            "    rev: v0.4.0\n"
            "    hooks:\n"
            "      - id: ruff\n"
            "      - id: ruff-format\n"
        )
        return files


class GitProvider(Provider):
    name = "git"
    display_name = "Git"
    category = "tooling"
    capabilities = ["vcs"]
