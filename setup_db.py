import os
from pathlib import Path
from unittest import mock

import alembic
import alembic.command
import alembic.config
from sqlalchemy import create_engine

from db_utils import connect_to_server, drop_connections, get_db_url

REPO_ROOT = Path(__file__).resolve().parent


def setup_db() -> None:
    db_url = get_db_url()

    # Connect to server default database
    with connect_to_server() as conn:
        drop_connections(conn, db_url.database)
        conn.exec_driver_sql(f"DROP DATABASE IF EXISTS {db_url.database};")
        conn.exec_driver_sql(f"CREATE DATABASE {db_url.database};")

    # Connect to database
    db_engine = create_engine(db_url, isolation_level="AUTOCOMMIT")
    with db_engine.connect() as conn:
        config = alembic.config.Config(REPO_ROOT / "alembic.ini", toml_file=REPO_ROOT / "pyproject.toml")
        alembic.command.stamp(config, "base")
        conn.exec_driver_sql("ALTER TABLE public.alembic_version ADD COLUMN deployment_tag INTEGER NULL;")
        conn.exec_driver_sql(
            "CREATE TABLE public.alembic_version_after ("
            "version_num VARCHAR(32) NOT NULL, "
            "napta_version VARCHAR(14) NULL, "
            "deployment_tag INTEGER NULL, "
            "CONSTRAINT pk_alembic_version_after PRIMARY KEY (version_num)"
            ");"
        )

        # Upgrade to initial version
        alembic.command.upgrade(config, "2be910b9f47e")
        with mock.patch.dict(os.environ, {"MIGRATION_STEP": "after"}):
            alembic.command.upgrade(config, "2be910b9f47e")


if __name__ == "__main__":
    setup_db()
