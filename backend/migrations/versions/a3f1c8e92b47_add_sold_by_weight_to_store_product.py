"""add soldByWeight to store_product

Revision ID: a3f1c8e92b47
Revises: 951e1d5c37a5
Create Date: 2026-06-05 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3f1c8e92b47'
down_revision = '951e1d5c37a5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('store_product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('soldByWeight', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table('store_product', schema=None) as batch_op:
        batch_op.drop_column('soldByWeight')
