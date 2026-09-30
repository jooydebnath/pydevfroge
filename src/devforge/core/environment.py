"""Environment (.env) management with secure secret generation."""

from __future__ import annotations

import secrets


def generate_secret_key(length: int = 50) -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def merge_env(base: dict[str, str], extra: dict[str, str]) -> dict[str, str]:
    merged = dict(base)
    merged.update(extra)
    return merged


def render_env(env: dict[str, str]) -> str:
    lines = []
    for key in sorted(env):
        value = env[key]
        # quote values containing spaces or # unless already quoted
        if (" " in value or "#" in value) and not (value.startswith('"') and value.endswith('"')):
            value = f'"{value}"'
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"


def base_env() -> dict[str, str]:
    return {
        "DEBUG": "True",
        "SECRET_KEY": generate_secret_key(),
    }
