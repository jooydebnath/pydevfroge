"""Cache / queue / broker service providers."""

from __future__ import annotations

from pathlib import Path

from devforge.core.context import ProjectContext
from devforge.providers.base import Provider, QuestionSpec


class RedisProvider(Provider):
    name = "redis"
    display_name = "Redis"
    category = "cache"
    description = "Redis cache and broker"
    packages = ["redis>=5.0"]
    capabilities = ["cache", "broker"]

    def environment(self, context: ProjectContext) -> dict[str, str]:
        if context.cache != "redis" and context.broker != "redis":
            return {}
        return {"REDIS_URL": "redis://redis:6379/0"}

    def docker_service(self, context: ProjectContext) -> dict | None:
        if not context.docker:
            return None
        if context.cache != "redis" and context.broker != "redis":
            return None
        return {"name": "redis", "image": "redis:7", "ports": ["6379:6379"]}


class NoneCacheProvider(Provider):
    name = "none-cache"
    display_name = "None"
    category = "cache"
    capabilities = ["cache"]


class CeleryProvider(Provider):
    name = "celery"
    display_name = "Celery"
    category = "queue"
    description = "Celery distributed task queue"
    packages = ["celery>=5.3"]
    requires = ["redis"]
    capabilities = ["queue", "background_tasks"]

    def questions(self, context: ProjectContext) -> list[QuestionSpec]:
        if context.task_queue != "celery":
            return []
        return [
            QuestionSpec(
                key="celery_beat",
                prompt="Enable Celery beat scheduler?",
                kind="confirm",
                default=True,
            ),
        ]

    def packages_for(self, context: ProjectContext) -> list[str]:
        if context.task_queue != "celery":
            return []
        pkgs = list(self.packages)
        if context.broker == "rabbitmq" or context.cache == "rabbitmq":
            pkgs.append("librabbitmq>=2.0")
        else:
            pkgs.append("redis>=5.0")
        return pkgs

    def environment(self, context: ProjectContext) -> dict[str, str]:
        if context.task_queue != "celery":
            return {}
        broker = (
            "redis://redis:6379/0"
            if context.broker in ("redis", "none", "") or context.cache == "redis"
            else "amqp://guest:guest@rabbitmq:5672//"
        )
        return {"CELERY_BROKER_URL": broker, "CELERY_RESULT_BACKEND": broker}

    def validate(self, context: ProjectContext) -> list[str]:
        if context.task_queue != "celery":
            return []
        if context.broker in ("none", "", None) and context.cache not in ("redis", "rabbitmq"):
            return ["Celery requires a broker (Redis or RabbitMQ)."]
        return []

    def generate(
        self, context: ProjectContext, project_dir: Path, files: dict[str, str]
    ) -> dict[str, str]:
        if context.task_queue != "celery":
            return files
        files["src/celery_app.py"] = (
            "import os\nfrom celery import Celery\n"
            'app = Celery("proj", broker=os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0"))\n'
            'app.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")\n'
        )
        return files

    def docker_service(self, context: ProjectContext) -> dict | None:
        if context.task_queue != "celery" or not context.docker:
            return None
        broker_svc = (
            "rabbitmq" if context.broker == "rabbitmq" or context.cache == "rabbitmq" else "redis"
        )
        return {
            "name": "worker",
            "build": ".",
            "command": "celery -A src.celery_app:app worker --loglevel=info",
            "env_file": ".env",
            "depends_on": [broker_svc],
        }


class RQProvider(Provider):
    name = "rq"
    display_name = "RQ"
    category = "queue"
    packages = ["rq>=1.16", "redis>=5.0"]
    capabilities = ["queue", "background_tasks"]


class NoneQueueProvider(Provider):
    name = "none-queue"
    display_name = "None"
    category = "queue"
    capabilities = ["queue"]


class RabbitMQProvider(Provider):
    name = "rabbitmq"
    display_name = "RabbitMQ"
    category = "cache"
    description = "RabbitMQ broker"
    packages = ["pika>=1.3"]
    capabilities = ["broker", "queue-backend"]

    def docker_service(self, context: ProjectContext) -> dict | None:
        if not context.docker:
            return None
        if context.broker != "rabbitmq" and context.cache != "rabbitmq":
            return None
        return {"name": "rabbitmq", "image": "rabbitmq:3-management", "ports": ["5672:5672"]}
