"""Initial baseline schema

Revision ID: 001_initial
Revises: None
Create Date: 2026-02-26
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Baseline migration — captures the current schema as of v2.0.0.

    This migration is intentionally a no-op because the schema is already
    created by database.init_db().  Running this migration simply stamps the
    database as being at revision 001_initial so that future Alembic
    migrations can build on top of it.
    """
    # Tables already exist via init_db(); this is a baseline stamp.
    # Future migrations should use op.add_column / op.create_table etc.
    pass


def downgrade() -> None:
    # Downgrading from baseline would mean dropping ALL tables — intentionally
    # left as a no-op to prevent accidental data loss.
    pass
