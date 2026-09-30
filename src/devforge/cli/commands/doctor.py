"""Modular doctor system."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()


def _check(label: str, ok: bool | None, detail: str = "") -> str:
    mark = "✔" if ok is True else ("⚠" if ok is None else "✘")
    line = f"{label:14} {mark} {detail}".rstrip()
    color = "green" if ok is True else ("yellow" if ok is None else "red")
    console.print(f"[{color}]{line}[/{color}]")
    return mark


def run_doctor(path: Path) -> int:
    console.print(Panel("DevForge Doctor", expand=False))
    issues = 0

    _check("Python", True, sys.version.split()[0])
    venv = os.environ.get("VIRTUAL_ENV") or (path / ".venv").exists()
    if not _check("Virtual Env", bool(venv), os.environ.get("VIRTUAL_ENV", "")) == "✔":
        issues += 1
    if not _check("Git", shutil.which("git") is not None) == "✔":
        issues += 1
    if not _check("Docker", shutil.which("docker") is not None) == "✔":
        issues += 1

    console.print("\n[bold]Environment[/bold]")
    env_file = path / ".env"
    if env_file.exists():
        content = env_file.read_text()
        for key in ("SECRET_KEY", "DATABASE_URL", "DEBUG"):
            present = key in content
            _check(key, True if present else False)
            if not present and key != "DATABASE_URL":
                issues += 1
    else:
        console.print("[yellow].env not found[/yellow]")
        issues += 1

    console.print("\n[bold]Project[/bold]")
    manifest = path / ".devforge" / "project.yaml"
    _check("Manifest", manifest.exists())
    if not manifest.exists():
        issues += 1
    pyproject = path / "pyproject.toml"
    _check("Dependencies", pyproject.exists())
    if not pyproject.exists():
        issues += 1
    tests = path / "tests"
    _check("Tests", tests.exists())

    console.print(f"\n{issues} issue(s) found.")
    return issues
