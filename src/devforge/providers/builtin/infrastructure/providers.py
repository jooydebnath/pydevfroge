"""Infrastructure providers: Docker, GitHub Actions, Nginx."""

from __future__ import annotations

from devforge.core.context import ProjectContext
from devforge.providers.base import Provider, QuestionSpec


class DockerProvider(Provider):
    name = "docker"
    display_name = "Docker"
    category = "container"
    capabilities = ["container", "deployment"]

    def questions(self, context: ProjectContext) -> list[QuestionSpec]:
        if not context.docker:
            return []
        return [
            QuestionSpec(
                key="docker_services_note",
                prompt="Docker services are derived automatically from selected providers.",
                kind="text",
                default="",
            )
        ]

    def generate(self, context, project_dir, files):
        return files  # compose/dockerfile merged by Generator core


class GitHubActionsProvider(Provider):
    name = "github-actions"
    display_name = "GitHub Actions"
    category = "cicd"
    capabilities = ["cicd"]

    def generate(self, context, project_dir, files):
        if context.cicd != "github-actions":
            return files
        services = ""
        if context.database == "postgresql":
            services += (
                "    services:\n"
                "      postgres:\n"
                "        image: postgres:16\n"
                "        env:\n"
                "          POSTGRES_PASSWORD: postgres\n"
                "        ports: ['5432:5432']\n"
            )
        if context.cache == "redis" or context.broker == "redis":
            services += "      redis:\n        image: redis:7\n        ports: ['6379:6379']\n"
        files[".github/workflows/ci.yml"] = (
            "name: CI\n"
            "on: [push, pull_request]\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            f"{services}"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-python@v5\n"
            "        with:\n"
            f"          python-version: '{context.python_version}'\n"
            "      - run: pip install -e .[dev]\n"
            "      - run: pytest\n"
        )
        return files


class NoneCICDProvider(Provider):
    name = "none-cicd"
    display_name = "None"
    category = "cicd"
    capabilities = ["cicd"]


class NginxProvider(Provider):
    name = "nginx"
    display_name = "Nginx"
    category = "web_server"
    capabilities = ["web_server", "reverse_proxy"]

    def generate(self, context, project_dir, files):
        if context.web_server != "nginx":
            return files
        files["nginx.conf"] = (
            "server {\n  listen 80;\n  location / {\n    proxy_pass http://app:8000;\n  }\n}\n"
        )
        return files
