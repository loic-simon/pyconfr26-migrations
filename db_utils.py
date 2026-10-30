from collections.abc import Generator
from contextlib import contextmanager
from copy import replace
from functools import cache
from pathlib import Path

import alembic
import alembic.config
from sqlalchemy import URL, Connection, create_engine, make_url

REPO_ROOT = Path(__file__).resolve().parent


@cache
def get_db_url() -> URL:
    config = alembic.config.Config(REPO_ROOT / "alembic.ini", toml_file=REPO_ROOT / "pyproject.toml")
    return make_url(config.get_alembic_option("sqlalchemy.url"))


@contextmanager
def connect_to_server() -> Generator[Connection]:
    """Connect to PostgreSQL server default database"""
    server_url = replace(get_db_url(), database="postgres")
    server_engine = create_engine(server_url, isolation_level="AUTOCOMMIT")
    with server_engine.connect() as conn:
        yield conn


@contextmanager
def connect_to_tmp_database() -> Generator[Connection]:
    db_name = "_tmp_check_migrations"
    with connect_to_server() as server_conn:
        try:
            server_conn.exec_driver_sql(f"CREATE DATABASE {db_name};")
            tmp_engine = create_engine(replace(get_db_url(), database=db_name))
            with tmp_engine.connect() as conn:
                yield conn
        finally:
            drop_connections(server_conn, db_name)
            server_conn.exec_driver_sql(f"DROP DATABASE {db_name};")


def drop_connections(conn: Connection, db_name: str) -> None:
    """Connect to PostgreSQL server default database"""
    conn.exec_driver_sql(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}';")
