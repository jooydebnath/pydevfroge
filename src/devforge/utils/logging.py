"""Logging helpers — secrets are never printed."""

from __future__ import annotations

import logging

from rich.console import Console
from rich.logging import RichHandler

console = Console()

SECRET_KEYS = ("SECRET", "PASSWORD", "TOKEN", "KEY")


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, show_path=verbose)],
    )


def redact(mapping: dict) -> dict:
    out = {}
    for k, v in mapping.items():
        if any(s in k.upper() for s in SECRET_KEYS):
            out[k] = "***"
        else:
            out[k] = v
    return out
