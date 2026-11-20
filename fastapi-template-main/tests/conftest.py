from pathlib import Path

from alembic import command
from alembic.config import Config
import pytest


@pytest.fixture
def migration_config(tmp_path):
    project_dir = Path(__file__).resolve().parents[1]
    config = Config(str(project_dir / "alembic.ini"))
    config.attributes["database_path"] = tmp_path / "test.sqlite3"
    return config


@pytest.fixture
def database_path(migration_config):
    # Тестовая БД создаётся теми же миграциями, что и рабочая.
    command.upgrade(migration_config, "head")
    return migration_config.attributes["database_path"]
