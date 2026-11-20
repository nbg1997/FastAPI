import sqlite3
from contextlib import closing

from alembic import command


def test_initial_migration_matches_models(migration_config):
    command.upgrade(migration_config, "head")
    # check завершается ошибкой, если autogenerate нашёл новые операции.
    command.check(migration_config)


def test_upgrade_is_repeatable_and_downgrade_removes_table(migration_config):
    command.upgrade(migration_config, "head")
    path = migration_config.attributes["database_path"]
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("INSERT INTO task (title, done) VALUES (?, ?)", ("Сохраниться", 0))
        connection.commit()
    command.upgrade(migration_config, "head")
    with closing(sqlite3.connect(path)) as connection:
        assert connection.execute("SELECT title FROM task").fetchall() == [("Сохраниться",)]
        assert connection.execute("SELECT version_num FROM alembic_version").fetchone() == ("0001",)
    command.downgrade(migration_config, "base")
    with closing(sqlite3.connect(path)) as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        assert "task" not in tables
