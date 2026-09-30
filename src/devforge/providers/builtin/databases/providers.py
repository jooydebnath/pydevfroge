"""Database providers."""

from __future__ import annotations

from devforge.core.context import ProjectContext
from devforge.providers.base import Provider


class PostgreSQLProvider(Provider):
    name = "postgresql"
    display_name = "PostgreSQL"
    category = "database"
    description = "PostgreSQL relational database"
    packages = ["psycopg[binary]>=3.1"]
    conflicts = ["sqlite"]
    capabilities = ["database", "relational_database"]

    def environment(self, context: ProjectContext) -> dict[str, str]:
        if context.database != "postgresql":
            return {}
        return {"DATABASE_URL": "postgresql://postgres:postgres@db:5432/app"}

    def docker_service(self, context: ProjectContext) -> dict | None:
        if context.database != "postgresql" or not context.docker:
            return None
        return {
            "name": "db",
            "image": "postgres:16",
            "environment": {
                "POSTGRES_USER": "postgres",
                "POSTGRES_PASSWORD": "postgres",
                "POSTGRES_DB": "app",
            },
            "ports": ["5432:5432"],
            "volumes": ["pgdata:/var/lib/postgresql/data"],
        }


class MySQLProvider(Provider):
    name = "mysql"
    display_name = "MySQL"
    category = "database"
    description = "MySQL relational database"
    packages = ["pymysql>=1.1"]
    conflicts = ["sqlite"]
    capabilities = ["database", "relational_database"]

    def environment(self, context: ProjectContext) -> dict[str, str]:
        if context.database != "mysql":
            return {}
        return {"DATABASE_URL": "mysql://root:root@db:3306/app"}

    def docker_service(self, context: ProjectContext) -> dict | None:
        if context.database != "mysql" or not context.docker:
            return None
        return {
            "name": "db",
            "image": "mysql:8",
            "environment": {
                "MYSQL_ROOT_PASSWORD": "root",
                "MYSQL_DATABASE": "app",
            },
            "ports": ["3306:3306"],
            "volumes": ["mysqldata:/var/lib/mysql"],
        }


class SQLiteProvider(Provider):
    name = "sqlite"
    display_name = "SQLite"
    category = "database"
    description = "SQLite embedded database"
    packages: list[str] = []
    conflicts = ["postgresql", "mysql"]
    capabilities = ["database", "relational_database", "embedded"]

    def environment(self, context: ProjectContext) -> dict[str, str]:
        if context.database != "sqlite":
            return {}
        return {"DATABASE_URL": "sqlite:///db.sqlite3"}


class NoneDatabaseProvider(Provider):
    name = "none-database"
    display_name = "None"
    category = "database"
    capabilities = ["database"]
