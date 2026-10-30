"""Initial revision

Revision ID: 88702dc0536f
Revises:
Create Date: 2026-10-14 15:19:07.260314

"""

from collections.abc import Sequence
from typing import Literal

# revision identifiers, used by Alembic.
revision: str = "88702dc0536f"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade(*, step: Literal["before", "after"]) -> None:
    pass


def downgrade(*, step: Literal["before", "after"]) -> None:
    raise RuntimeError("Two-step migration framework does not handle downgrades!")
