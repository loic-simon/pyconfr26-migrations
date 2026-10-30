"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union, Literal

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade(*, step: Literal["before", "after"]) -> None:
    ${upgrades if upgrades else "pass"}


def downgrade(*, step: Literal["before", "after"]) -> None:
    raise RuntimeError("Two-step migration framework does not handle downgrades!")
