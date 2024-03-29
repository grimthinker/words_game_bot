"""correct gamerules

Revision ID: d53cfb49b376
Revises: 1fcc3125797b
Create Date: 2023-03-11 19:48:54.830613

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d53cfb49b376"
down_revision = "1fcc3125797b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "game_rules", sa.Column("similarity_valued", sa.Boolean(), nullable=False)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("game_rules", "similarity_valued")
    # ### end Alembic commands ###
