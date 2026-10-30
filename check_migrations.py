import pprint
import sys
from pathlib import Path

import comdab
from sqlalchemy import create_engine

from app.models.base import BaseModel
from db_utils import connect_to_tmp_database, get_db_url

REPO_ROOT = Path(__file__).resolve().parent


def main() -> None:
    db_url = get_db_url()
    real_db_engine = create_engine(db_url)

    with (
        real_db_engine.connect() as real_db_conn,
        connect_to_tmp_database() as schema_conn,
    ):
        BaseModel.metadata.create_all(schema_conn)

        reports = comdab.compare_databases(
            left_connection=schema_conn,
            right_connection=real_db_conn,
            rules={comdab.ROOT.tables["alembic_.+"]: "ignore"},  # Alembic tables, not in declared schema
        )
        pprint.pp(reports or "All good!", expand=True, indent=4)
        if reports:
            sys.exit(1)
        else:
            print("All good!")


if __name__ == "__main__":
    main()
