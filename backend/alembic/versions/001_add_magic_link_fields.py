"""add magic link fields

Revision ID: 001_magic_link
Revises:
Create Date: 2026-01-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_magic_link'
down_revision: Union[str, None] = '000_baseline'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add magic_link_token column
    op.add_column('users', sa.Column('magic_link_token', sa.String(255), nullable=True))
    # Add magic_link_expires column
    op.add_column('users', sa.Column('magic_link_expires', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'magic_link_expires')
    op.drop_column('users', 'magic_link_token')
