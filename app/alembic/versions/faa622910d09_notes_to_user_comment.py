"""Notes to user_comment

Revision ID: faa622910d09
Revises: 41290166298f
Create Date: 2026-10-20 15:35:01.212256

"""

from collections.abc import Sequence
from typing import Literal

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "faa622910d09"
down_revision: str | Sequence[str] | None = "41290166298f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade(*, step: Literal["before", "after"]) -> None:
    if step == "before":
        op.create_table(
            "user_comment",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("content", sa.String(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        )
        op.execute(
            """CREATE OR REPLACE FUNCTION tmp_copy_notes_to_user_comment_fn() RETURNS TRIGGER
                AS $fbd$
                BEGIN
                    IF OLD.notes IS NOT NULL THEN
                        DELETE FROM user_comment WHERE user_id = NEW.id AND content = OLD.notes;
                    END IF;
                    IF NEW.notes IS NOT NULL THEN
                        INSERT INTO user_comment (user_id, content) VALUES (NEW.id, NEW.notes);
                    END IF;
                    RETURN NEW;
                END;
                $fbd$ LANGUAGE plpgsql;
            """
        )
        op.execute(
            """CREATE OR REPLACE FUNCTION tmp_copy_user_comment_to_notes_fn() RETURNS TRIGGER
                AS $fbd$
                BEGIN
                    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
                        UPDATE public.user SET notes = NEW.content WHERE id = NEW.user_id;
                    ELSE -- DELETE
                        UPDATE public.user SET notes = NULL WHERE id = NEW.user_id AND notes = OLD.content;
                    END IF;
                    RETURN NEW;
                END;
                $fbd$ LANGUAGE plpgsql;
            """
        )
        op.execute(
            """CREATE TRIGGER tmp_copy_notes_to_user_comment
            AFTER INSERT OR UPDATE OF notes ON public.user
            FOR EACH ROW WHEN (pg_trigger_depth() < 1)
            EXECUTE FUNCTION tmp_copy_notes_to_user_comment_fn();
            """
        )
        op.execute(
            """CREATE TRIGGER tmp_copy_user_comment_to_notes
            AFTER INSERT OR UPDATE OR DELETE ON public.user_comment
            FOR EACH ROW WHEN (pg_trigger_depth() < 1)
            EXECUTE FUNCTION tmp_copy_user_comment_to_notes_fn();
            """
        )
    else:
        op.execute("DROP TRIGGER tmp_copy_notes_to_user_comment ON public.user;")
        op.execute("DROP TRIGGER tmp_copy_user_comment_to_notes ON public.user_comment;")
        op.drop_column("user", "notes")


def downgrade(*, step: Literal["before", "after"]) -> None:
    raise RuntimeError("Two-step migration framework does not handle downgrades!")
