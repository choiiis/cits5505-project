"""add auth tokens and email verification

Revision ID: ead2a5f0b911
Revises: 8ac2dfe8e178
Create Date: 2026-05-16 17:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "ead2a5f0b911"
down_revision = "8ac2dfe8e178"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("email_verified_at", sa.DateTime(), nullable=True))

    op.execute("UPDATE user SET email_verified_at = CURRENT_TIMESTAMP")

    op.create_table(
        "auth_token",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("purpose", sa.String(length=40), nullable=False),
        sa.Column("new_email", sa.String(length=120), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("auth_token", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_auth_token_expires_at"), ["expires_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_auth_token_purpose"), ["purpose"], unique=False)
        batch_op.create_index(batch_op.f("ix_auth_token_token_hash"), ["token_hash"], unique=True)
        batch_op.create_index(batch_op.f("ix_auth_token_user_id"), ["user_id"], unique=False)


def downgrade():
    with op.batch_alter_table("auth_token", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_auth_token_user_id"))
        batch_op.drop_index(batch_op.f("ix_auth_token_token_hash"))
        batch_op.drop_index(batch_op.f("ix_auth_token_purpose"))
        batch_op.drop_index(batch_op.f("ix_auth_token_expires_at"))

    op.drop_table("auth_token")

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_column("email_verified_at")
