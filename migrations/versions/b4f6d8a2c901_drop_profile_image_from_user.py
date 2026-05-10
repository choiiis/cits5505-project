"""drop profile image from user

Revision ID: b4f6d8a2c901
Revises: 7c2f8e1a9b43
Create Date: 2026-05-10 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "b4f6d8a2c901"
down_revision = "7c2f8e1a9b43"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("profile_image")


def downgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("profile_image", sa.String(length=255), nullable=True))
