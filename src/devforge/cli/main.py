"""Typer CLI — consumer of the core Python API."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from devforge import __version__
from devforge.builder import ProjectBuilder
from devforge.cli.wizard import run_wizard
from devforge.core.exceptions import DevForgeError
from devforge.utils.logging import setup_logging

app = typer.Typer(
    name="devforge", help="Dynamic Python project bootstrap & automation.", no_args_is_help=False
)
console = Console()


def _builder() -> ProjectBuilder:
    return ProjectBuilder()


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose diagnostics."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be created."),
    output: str | None = typer.Option(None, "--output", "-o", help="Output directory."),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", help="Skip wizard (use defaults)."
    ),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing files."),
) -> None:
    setup_logging(verbose)
    if ctx.invoked_subcommand is not None:
        return
    # `devforge` with no subcommand -> interactive wizard
    try:
        builder = _builder()
        if non_interactive:
            context = builder.configure(name="my-project")
        else:
            context = run_wizard(builder.registry)
            builder.configure(**context.model_dump())
        if dry_run:
            _show_dry_run(builder)
            return
        dest = Path(output) if output else Path.cwd()
        with console.status("Creating project..."):
            result = builder.generate(dest, overwrite=overwrite)
        _show_success(builder, result)
    except DevForgeError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc


@app.command()
def create(
    name: str = typer.Option("my-project", help="Project name."),
    framework: str = typer.Option("none", help="django|fastapi|flask|none"),
    database: str = typer.Option("none", help="postgresql|mysql|sqlite|none"),
    cache: str = typer.Option("none", help="redis|none"),
    task_queue: str = typer.Option("none", help="celery|rq|none"),
    broker: str = typer.Option("none", help="redis|rabbitmq|none"),
    authentication: str = typer.Option("none"),
    testing: str = typer.Option("pytest"),
    formatter: str = typer.Option("ruff"),
    docker: bool = typer.Option(False),
    cicd: str = typer.Option("none"),
    output: str = typer.Option(".", help="Output directory."),
    overwrite: bool = typer.Option(False),
    dry_run: bool = typer.Option(False, "--dry-run"),
    verbose: bool = typer.Option(False, "--verbose"),
    install: bool = typer.Option(False, help="pip install dependencies after generation."),
) -> None:
    """Non-interactive project creation."""
    setup_logging(verbose)
    try:
        builder = _builder()
        builder.configure(
            name=name,
            framework=framework,
            database=database,
            cache=cache,
            task_queue=task_queue,
            broker=broker,
            authentication=authentication,
            testing=testing,
            formatter=formatter,
            docker=docker,
            cicd=cicd,
        )
        if dry_run:
            _show_dry_run(builder)
            return
        with console.status("Creating project..."):
            result = builder.generate(output, overwrite=overwrite, install=install)
        _show_success(builder, result)
    except DevForgeError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc


@app.command()
def doctor(
    path: str = typer.Option(".", help="Project directory to inspect."),
    verbose: bool = typer.Option(False, "--verbose"),
) -> None:
    """Inspect the current project for common issues."""
    from devforge.cli.commands.doctor import run_doctor

    setup_logging(verbose)
    run_doctor(Path(path))


@app.command()
def info() -> None:
    """Show supported providers."""
    builder = _builder()
    table = Table(title=f"DevForge {__version__} providers")
    table.add_column("Category")
    table.add_column("Providers")
    cats: dict[str, list[str]] = {}
    for p in builder.registry.all():
        cats.setdefault(p.category, []).append(p.display_name)
    for cat in sorted(cats):
        table.add_row(cat, ", ".join(sorted(cats[cat])))
    console.print(table)


def _show_dry_run(builder: ProjectBuilder) -> None:
    plan = builder.dry_run()
    console.print(Panel("Dry run — nothing was modified", border_style="yellow"))
    console.print("[bold]Would create:[/bold]")
    for f in plan["files"]:
        console.print(f"  ✓ {f}", markup=False)
    console.print("[bold]Would install:[/bold]")
    for p in plan["packages"] or ["(no dependencies)"]:
        console.print(f"  ✓ {p}", markup=False)
    console.print(f"[dim]Env keys: {', '.join(plan['env_keys'])}[/dim]")


def _show_success(builder: ProjectBuilder, result) -> None:
    ctx = builder.context
    lines = (
        f"[bold]Project[/bold]       {ctx.name}\n"
        f"[bold]Framework[/bold]     {ctx.framework}\n"
        f"[bold]Database[/bold]      {ctx.database}\n"
        f"[bold]Cache[/bold]         {ctx.cache}\n"
        f"[bold]Queue[/bold]         {ctx.task_queue}\n"
        f"[bold]Auth[/bold]          {ctx.authentication}\n"
        f"[bold]Testing[/bold]       {ctx.testing}\n"
        f"[bold]Formatter[/bold]     {ctx.formatter}\n"
        f"[bold]Docker[/bold]        {'Enabled' if ctx.docker else 'Disabled'}\n"
        f"[bold]CI/CD[/bold]         {ctx.cicd}"
    )
    console.print(Panel("🎉 PROJECT CREATED SUCCESSFULLY", expand=False, border_style="green"))
    console.print(Panel(lines, title="Summary", expand=False))
    console.print(f"[green]✔ Created {len(result.files)} files in {result.project_dir}[/green]")
    console.print("\n[bold]Next steps:[/bold]\n")
    console.print(f"  cd {result.project_dir}")
    console.print("  python -m venv .venv && source .venv/bin/activate")
    console.print("  pip install -e .[dev]")
    console.print("  devforge doctor")
    console.print("\nHappy coding! 🚀")


app.command(name="sync")(info)

if __name__ == "__main__":
    app()
