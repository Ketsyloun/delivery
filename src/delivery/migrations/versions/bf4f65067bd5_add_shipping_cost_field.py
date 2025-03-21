"""Add shipping_cost field

Revision ID: bf4f65067bd5
Revises: 4180954b4b2f
Create Date: 2025-03-13 14:07:20.819194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf4f65067bd5'
down_revision: Union[str, None] = '4180954b4b2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('parcels', sa.Column('shipping_cost', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('parcels', 'shipping_cost')
    # ### end Alembic commands ###
