"""Generator + manifest tests."""

import tomllib

from devforge.builder import ProjectBuilder


def test_plan_files(tmp_path):
    b = ProjectBuilder()
    b.configure(name="demo", framework="fastapi", database="sqlite", testing="pytest")
    plan = b.dry_run()
    assert "pyproject.toml" in plan["files"]
    assert ".env" in plan["files"]
    assert any("fastapi" in p for p in plan["packages"])


def test_generate_fastapi_sqlite(tmp_path):
    b = ProjectBuilder()
    b.configure(name="demo-api", framework="fastapi", database="sqlite", testing="pytest")
    result = b.generate(tmp_path, overwrite=True)
    assert (result.project_dir / "pyproject.toml").exists()
    assert (result.project_dir / ".env").exists()
    assert (result.project_dir / ".env.example").exists()
    assert (result.project_dir / "src" / "main.py").exists()
    assert (result.project_dir / "tests" / "test_health.py").exists()
    assert (result.project_dir / ".devforge" / "project.yaml").exists()
    content = (result.project_dir / "pyproject.toml").read_text()
    assert "fastapi" in content


def test_generate_full_stack(tmp_path):
    b = ProjectBuilder()
    b.configure(
        name="ecommerce-api",
        framework="django",
        database="postgresql",
        cache="redis",
        broker="redis",
        task_queue="celery",
        authentication="jwt",
        testing="pytest",
        formatter="ruff",
        docker=True,
        cicd="github-actions",
    )
    result = b.generate(tmp_path, overwrite=True)
    for rel in [
        "pyproject.toml",
        "Dockerfile",
        "docker-compose.yml",
        ".gitignore",
        ".github/workflows/ci.yml",
        "src/settings.py",
        "src/celery_app.py",
    ]:
        assert (result.project_dir / rel).exists(), rel
    compose = (result.project_dir / "docker-compose.yml").read_text()
    assert "db" in compose and "redis" in compose
    pyproject = (result.project_dir / "pyproject.toml").read_text()
    for pkg in ["django", "psycopg", "celery", "redis"]:
        assert pkg in pyproject.lower(), pkg


def test_generated_pyproject_valid_toml(tmp_path):
    b = ProjectBuilder()
    b.configure(name="t", framework="flask", database="sqlite")
    result = b.generate(tmp_path, overwrite=True)
    with open(result.project_dir / "pyproject.toml", "rb") as f:
        tomllib.load(f)
