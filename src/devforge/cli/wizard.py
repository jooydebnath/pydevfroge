"""Dynamic wizard — providers contribute questions, core asks them."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel

from devforge.core.context import ProjectContext
from devforge.core.registry import ProviderRegistry
from devforge.core.resolver import DependencyResolver

console = Console()


def _ask_select(prompt: str, options: list[str], default: str | None) -> str:
    console.print(f"[bold]? {prompt}[/bold] [dim]({', '.join(options)})[/dim]")
    if default:
        console.print(f"[dim]Default: {default}[/dim]")
    while True:
        raw = typer.prompt(">", default=default or (options[0] if options else ""))
        raw = str(raw).strip()
        # case-insensitive match
        for opt in options:
            if raw.lower() == opt.lower():
                return opt
        console.print(f"[red]Choose one of: {', '.join(options)}[/red]")


def _ask_confirm(prompt: str, default: bool = True) -> bool:
    return typer.confirm(f"? {prompt}", default=default)


def _ask_text(prompt: str, default: str = "") -> str:
    return typer.prompt(f"? {prompt}", default=default)


BANNER = """\
  🚀 DevForge
  Project Bootstrap & Automation"""


def show_banner() -> None:
    console.print(Panel(BANNER, expand=False, border_style="cyan"))


def _category_options(
    registry: ProviderRegistry, category: str, none_label: str = "None"
) -> list[str]:
    providers = registry.options(category)
    # map internal none-* providers to "None"
    names: list[str] = []
    for p in providers:
        if p.name.startswith("none"):
            names.append("None")
        else:
            names.append(p.name)
    # dedupe, stable
    seen: list[str] = []
    for n in names:
        if n not in seen:
            seen.append(n)
    return seen


def _normalize_none(value: str, registry: ProviderRegistry, category: str) -> str:
    if value == "None":
        for p in registry.options(category):
            if p.name.startswith("none"):
                return p.name
        return "none"
    return value


def run_wizard(
    registry: ProviderRegistry,
    *,
    ask: Callable | None = None,  # for tests: ask(prompt, options, default) -> str
    initial: dict[str, Any] | None = None,
) -> ProjectContext:
    """Run the dynamic interactive wizard and return a ProjectContext."""
    show_banner()
    data: dict[str, Any] = dict(initial or {})

    def do_select(prompt: str, options: list[str], default: Any = None) -> str:
        if ask is not None:
            return str(ask(prompt, options, default))
        return _ask_select(prompt, options, str(default) if default else None)

    def do_confirm(prompt: str, default: bool = True) -> bool:
        if ask is not None:
            return bool(
                ask(prompt, ["Yes", "No"], "Yes" if default else "No") in ("Yes", True, "yes")
            )
        return _ask_confirm(prompt, default)

    def do_text(prompt: str, default: str = "") -> str:
        if ask is not None:
            r = ask(prompt, [], default)
            return str(r) if r else default
        return _ask_text(prompt, default)

    if "name" not in data:
        data["name"] = do_text("Project name", "my-project")
    if "language" not in data:
        data["language"] = "python"
    if "python_version" not in data:
        data["python_version"] = do_select("Python version", ["3.11", "3.12", "3.13"], "3.12")
    if "framework" not in data:
        # friendly display: map names; keep raw names for django/fastapi/flask
        raw = do_select("Framework", ["Django", "FastAPI", "Flask", "None"], "Django")
        data["framework"] = {"Django": "django", "FastAPI": "fastapi", "Flask": "flask"}.get(
            raw, "none"
        )
    if "database" not in data:
        raw = do_select("Database", ["PostgreSQL", "MySQL", "SQLite", "None"], "PostgreSQL")
        data["database"] = {"PostgreSQL": "postgresql", "MySQL": "mysql", "SQLite": "sqlite"}.get(
            raw, "none"
        )
    if "authentication" not in data:
        raw = do_select("Authentication", ["JWT", "Session", "OAuth2", "None"], "None")
        data["authentication"] = {"JWT": "jwt", "Session": "session", "OAuth2": "oauth2"}.get(
            raw, "none"
        )
    if "cache" not in data:
        raw = do_select("Cache", ["Redis", "None"], "None")
        data["cache"] = {"Redis": "redis"}.get(raw, "none")
    if "task_queue" not in data:
        raw = do_select("Background task system", ["Celery", "RQ", "None"], "None")
        data["task_queue"] = {"Celery": "celery", "RQ": "rq"}.get(raw, "none")

    # resolver-driven dynamic question: celery broker
    tmp = ProjectContext(**{**_defaults(), **data})
    resolver = DependencyResolver(registry)
    resolution = resolver.resolve(tmp)
    for choice in resolution.needed_choices:
        picked = do_select(choice["prompt"], choice["options"], choice.get("default"))
        data[choice["key"]] = picked

    if "testing" not in data:
        raw = do_select("Testing", ["pytest", "unittest", "None"], "pytest")
        data["testing"] = raw.lower() if raw != "None" else "none"
    if "formatter" not in data:
        raw = do_select("Code quality", ["Ruff", "Ruff + pre-commit", "None"], "Ruff")
        if raw == "Ruff + pre-commit":
            data["formatter"] = "ruff"
            data["use_pre_commit"] = True
        elif raw == "Ruff":
            data["formatter"] = "ruff"
        else:
            data["formatter"] = "none"
    if "docker" not in data:
        data["docker"] = do_confirm("Enable Docker?", default=True)
    if "cicd" not in data:
        raw = do_select("CI/CD", ["GitHub Actions", "None"], "None")
        data["cicd"] = {"GitHub Actions": "github-actions"}.get(raw, "none")

    # provider-contributed questions (dynamic, no core hard-coding of extras)
    ctx = ProjectContext(**{**_defaults(), **data})
    for provider in registry.active_for(ctx):
        for q in provider.questions(ctx):
            if q.kind == "text" and not q.options:
                continue  # informational notes
            if q.key in data:
                continue
            if q.condition is not None and not q.condition(ctx):
                continue
            if q.kind == "confirm":
                data[q.key] = do_confirm(
                    q.prompt, bool(q.default) if q.default is not None else True
                )
            elif q.kind == "text":
                data[q.key] = do_text(q.prompt, str(q.default or ""))
            else:
                data[q.key] = do_select(q.prompt, q.options, q.default)
            # refresh ctx extras
            ctx = ProjectContext(**{**_defaults(), **data})

    # split extras
    core_keys = set(ProjectContext.model_fields.keys())
    extras = {k: v for k, v in data.items() if k not in core_keys}
    core_data = {k: v for k, v in data.items() if k in core_keys}
    core_data["extras"] = {**(core_data.get("extras", {})), **extras}
    return ProjectContext(**core_data)


def _defaults() -> dict[str, Any]:
    return {
        "name": "my-project",
        "language": "python",
        "python_version": "3.12",
        "framework": "none",
        "database": "none",
        "authentication": "none",
        "cache": "none",
        "task_queue": "none",
        "broker": "none",
        "testing": "pytest",
        "formatter": "ruff",
        "docker": False,
        "cicd": "none",
    }
