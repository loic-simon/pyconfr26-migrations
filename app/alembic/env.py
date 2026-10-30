import logging
import os
from logging.config import fileConfig
from typing import Literal

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.models.base import BaseModel

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger("alembic.env")


def run_migrations_offline() -> None:
    raise NotImplementedError()


def run_migrations_online() -> None:
    step: Literal["before", "after"] = os.getenv("MIGRATION_STEP", "before")
    version_table = "alembic_version_after" if step == "after" else "alembic_version"

    deployment_tag = int(os.getenv("DEPLOYMENT_TAG") or "0")

    engine = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with engine.connect() as connection:
        if deployment_tag and step == "after":
            db_tag = connection.exec_driver_sql(f"SELECT deployment_tag FROM public.{version_table};").scalar_one()
            if db_tag and db_tag >= deployment_tag:
                logger.info(f"Database has deployment_tag={db_tag} >= {deployment_tag}, skipping upgrade")
                return

        context.configure(
            connection=connection,
            target_metadata=BaseModel.metadata,
            version_table=version_table,
            include_object=lambda obj, *_: getattr(obj, "name", None) != "alembic_version_after",
        )

        with context.begin_transaction():
            context.run_migrations(step=step)
            if deployment_tag:
                connection.exec_driver_sql(f"UPDATE public.{version_table} SET deployment_tag = '{deployment_tag!s}';")
                connection.commit()
                logger.info(f"{version_table}.deployment_tag set to {deployment_tag}")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
