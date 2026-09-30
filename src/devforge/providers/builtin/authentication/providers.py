"""Authentication providers."""

from __future__ import annotations

from devforge.core.context import ProjectContext
from devforge.providers.base import Provider


class JWTProvider(Provider):
    name = "jwt"
    display_name = "JWT"
    category = "authentication"
    description = "JSON Web Token authentication"
    packages = ["pyjwt>=2.8"]
    capabilities = ["authentication", "stateless"]

    def packages_for(self, context: ProjectContext) -> list[str]:
        if context.authentication != "jwt":
            return []
        if context.framework == "django":
            return ["djangorestframework-simplejwt>=5.3"]
        if context.framework == "fastapi":
            return ["python-jose[cryptography]>=3.3", "passlib[bcrypt]>=1.7"]
        return list(self.packages)

    def environment(self, context: ProjectContext) -> dict[str, str]:
        if context.authentication != "jwt":
            return {}
        return {"JWT_ALGORITHM": "HS256", "JWT_EXPIRATION": "3600"}


class SessionAuthProvider(Provider):
    name = "session"
    display_name = "Session"
    category = "authentication"
    capabilities = ["authentication", "stateful"]


class OAuth2Provider(Provider):
    name = "oauth2"
    display_name = "OAuth2"
    category = "authentication"
    packages = ["authlib>=1.3"]
    capabilities = ["authentication", "oauth"]

    def environment(self, context: ProjectContext) -> dict[str, str]:
        if context.authentication != "oauth2":
            return {}
        return {"OAUTH_CLIENT_ID": "", "OAUTH_CLIENT_SECRET": ""}


class NoneAuthProvider(Provider):
    name = "none-auth"
    display_name = "None"
    category = "authentication"
    capabilities = ["authentication"]
