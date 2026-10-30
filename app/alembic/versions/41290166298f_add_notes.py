"""Add notes

Revision ID: 41290166298f
Revises: 2be910b9f47e
Create Date: 2026-10-14 22:31:43.283409

"""

from collections.abc import Sequence
from typing import Literal

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "41290166298f"
down_revision: str | Sequence[str] | None = "2be910b9f47e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade(*, step: Literal["before", "after"]) -> None:
    if step == "before":
        op.add_column("user", sa.Column("notes", sa.String(), nullable=True))


def upgrade_after() -> None:
    pass


def downgrade(*, step: Literal["before", "after"]) -> None:
    raise RuntimeError("Two-step migration framework does not handle downgrades!")
