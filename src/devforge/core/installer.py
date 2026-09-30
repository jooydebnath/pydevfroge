"""Dependency installer (pip) — kept separate from generation."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from devforge.core.exceptions import InstallationError


def install_packages(packages: list[str], *, target_dir: Path | None = None) -> None:
    if not packages:
        return
    cmd = [sys.executable, "-m", "pip", "install", *packages]
    try:
        subprocess.run(
            cmd,
            check=True,
            cwd=str(target_dir) if target_dir else None,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise InstallationError(f"pip install failed: {exc.stderr[-2000:]}") from exc


def create_venv(venv_dir: Path) -> Path:
    import venv

    venv.create(str(venv_dir), with_pip=True)
    return venv_dir
