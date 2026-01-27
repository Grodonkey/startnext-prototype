"""add avatar_url to users

Revision ID: 011_avatar_url
Revises: 010_ai_drafts_session
Create Date: 2026-01-27

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '011_avatar_url'
down_revision: Union[str, None] = '010_ai_drafts_session'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('avatar_url', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'avatar_url')
