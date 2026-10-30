"""Create user table

Revision ID: 2be910b9f47e
Revises: 88702dc0536f
Create Date: 2026-10-14 15:19:17.581539

"""

from collections.abc import Sequence
from typing import Literal

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2be910b9f47e"
down_revision: str | Sequence[str] | None = "88702dc0536f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade(*, step: Literal["before", "after"]) -> None:
    if step == "before":
        op.create_table(
            "user",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade(*, step: Literal["before", "after"]) -> None:
    raise RuntimeError("Two-step migration framework does not handle downgrades!")
