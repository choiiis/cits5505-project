"""Add collection subscriptions

Revision ID: 2d9a3f4b6c71
Revises: ead2a5f0b911
Create Date: 2026-05-16 16:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "2d9a3f4b6c71"
down_revision = "ead2a5f0b911"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "collection_subscription",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("collection_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["collection_id"], ["bookmark_collection.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "collection_id",
            "user_id",
            name="unique_collection_subscription_per_user",
        ),
    )


def downgrade():
    op.drop_table("collection_subscription")
