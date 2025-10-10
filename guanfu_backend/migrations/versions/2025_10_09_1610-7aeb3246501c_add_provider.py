"""add provider

Revision ID: 7aeb3246501c
Revises: 0f01908e6629
Create Date: 2025-10-09 16:10:03.321913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7aeb3246501c'
down_revision: Union[str, Sequence[str], None] = '0f01908e6629'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('supplies', sa.Column('spam_warn', sa.Boolean(), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('supplies', 'spam_warn')
