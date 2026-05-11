"""repair owner profile schema

Revision ID: c9e4a1d7b2f0
Revises: b4f6d8a2c901
Create Date: 2026-05-11 11:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "c9e4a1d7b2f0"
down_revision = "b4f6d8a2c901"
branch_labels = None
depends_on = None


def _column_names(table_name):
    inspector = sa.inspect(op.get_bind())
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade():
    columns = _column_names("user")

    with op.batch_alter_table("user", schema=None) as batch_op:
        if "profile_image" not in columns:
            batch_op.add_column(sa.Column("profile_image", sa.String(length=255), nullable=True))

        if "restaurant_name" in columns:
            batch_op.drop_column("restaurant_name")


def downgrade():
    pass
