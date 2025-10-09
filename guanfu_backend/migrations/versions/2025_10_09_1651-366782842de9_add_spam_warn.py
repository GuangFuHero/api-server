"""add spam_warn

Revision ID: 366782842de9
Revises: 7aeb3246501c
Create Date: 2025-10-09 16:51:09.008644

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '366782842de9'
down_revision: Union[str, Sequence[str], None] = '7aeb3246501c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "supply_providers",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=False),
        sa.Column("supply_item_id", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=False),
        sa.Column("notes", sa.String(), nullable=False, server_default=sa.text("''")),
        sa.Column("provide_count", sa.Integer(), nullable=False),
        sa.Column("provide_unit", sa.String(), nullable=True),
        sa.Column('created_at', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # index: supply_item_id
    op.create_index(
        "idx_supply_providers_supply_item_id",
        "supply_providers",
        ["supply_item_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_supply_providers_supply_item_id", table_name="supply_providers")
    op.drop_table("supply_providers")
