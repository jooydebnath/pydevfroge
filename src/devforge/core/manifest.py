"""Project manifest (.devforge/project.yaml)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from devforge.core.context import ProjectContext

MANIFEST_DIR = ".devforge"
MANIFEST_FILE = "project.yaml"


def context_to_manifest(context: ProjectContext, devforge_version: str) -> dict[str, Any]:
    return {
        "devforge_version": devforge_version,
        "project": {"name": context.name},
        "language": {"name": context.language, "version": context.python_version},
        "framework": {"provider": context.framework},
        "database": {"provider": context.database},
        "authentication": {"provider": context.authentication},
        "cache": {"provider": context.cache},
        "queue": {"provider": context.task_queue, "broker": context.broker},
        "services": [
            s
            for s in [context.cache, context.task_queue, context.broker]
            if s not in ("none", "", None)
        ],
        "tools": [
            t
            for t in [
                context.testing,
                context.formatter,
                "pre-commit" if context.use_pre_commit else "none",
                "git" if context.git else "none",
            ]
            if t not in ("none", "", None)
        ],
        "infrastructure": {
            "docker": bool(context.docker),
            "cicd": context.cicd,
        },
        "extras": dict(context.extras),
    }


def write_manifest(project_dir: Path, context: ProjectContext, devforge_version: str) -> Path:
    data = context_to_manifest(context, devforge_version)
    target_dir = project_dir / MANIFEST_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / MANIFEST_FILE
    target.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return target


def read_manifest(project_dir: Path) -> dict[str, Any]:
    target = Path(project_dir) / MANIFEST_DIR / MANIFEST_FILE
    return yaml.safe_load(target.read_text(encoding="utf-8"))
