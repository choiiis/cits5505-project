"""add owner contact fields to user

Revision ID: 7c2f8e1a9b43
Revises: 4883d5ccf723
Create Date: 2026-05-10 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "7c2f8e1a9b43"
down_revision = "4883d5ccf723"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("abn_number", sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column("contact_number", sa.String(length=50), nullable=True))


def downgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("contact_number")
        batch_op.drop_column("abn_number")
