"""DevForge custom exceptions."""


class DevForgeError(Exception):
    """Base error for all DevForge failures."""


class ProviderError(DevForgeError):
    """Raised when a provider fails or is misconfigured."""


class ConfigurationError(DevForgeError):
    """Raised for invalid project configuration."""


class DependencyError(DevForgeError):
    """Raised when dependencies cannot be resolved."""


class ConflictError(DevForgeError):
    """Raised when providers conflict with each other."""

    def __init__(self, message: str, *, options: list[str] | None = None) -> None:
        super().__init__(message)
        self.options = options or []


class GenerationError(DevForgeError):
    """Raised when project generation fails."""


class InstallationError(DevForgeError):
    """Raised when dependency installation fails."""


class ValidationError(DevForgeError):
    """Raised when validation fails."""
