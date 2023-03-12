"""added gamerules

Revision ID: 1fcc3125797b
Revises: 8e5451f965af
Create Date: 2023-03-11 05:32:19.084905

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1fcc3125797b"
down_revision = "8e5451f965af"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "game_rules",
        sa.Column("session_id", sa.BigInteger(), nullable=False),
        sa.Column("max_diff_rule", sa.Boolean(), nullable=False),
        sa.Column("max_diff_val", sa.BigInteger(), nullable=False),
        sa.Column("min_diff_rule", sa.Boolean(), nullable=False),
        sa.Column("min_diff_val", sa.BigInteger(), nullable=False),
        sa.Column("max_long_rule", sa.Boolean(), nullable=False),
        sa.Column("max_long_val", sa.BigInteger(), nullable=False),
        sa.Column("min_long_rule", sa.Boolean(), nullable=False),
        sa.Column("min_long_val", sa.BigInteger(), nullable=False),
        sa.Column("custom_vote_time", sa.BigInteger(), nullable=True),
        sa.Column("custom_word_time", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_id"], ["game_sessions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("session_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("game_rules")
    # ### end Alembic commands ###