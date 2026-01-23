"""baseline - existing database schema

Revision ID: 000_baseline
Revises:
Create Date: 2026-01-22

This is a baseline migration for existing databases that were created
without alembic. It does nothing but establishes a starting point.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000_baseline'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This is a baseline migration - the schema already exists
    # We just need to establish the alembic_version table
    pass


def downgrade() -> None:
    # Cannot downgrade from baseline
    pass
