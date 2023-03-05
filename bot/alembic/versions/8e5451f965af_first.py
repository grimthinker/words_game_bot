"""first

Revision ID: 8e5451f965af
Revises: 
Create Date: 2023-02-28 16:40:05.177946

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e5451f965af'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('email', sa.String(length=60), nullable=False),
    sa.Column('password', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('chats',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('players',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('game_sessions',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('creator_id', sa.BigInteger(), nullable=False),
    sa.Column('state', sa.Integer(), nullable=False),
    sa.Column('time_updated', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['creator_id'], ['players.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('association_players_sessions',
    sa.Column('player_id', sa.BigInteger(), nullable=False),
    sa.Column('session_id', sa.BigInteger(), nullable=False),
    sa.Column('points', sa.Integer(), nullable=False),
    sa.Column('is_dropped_out', sa.Boolean(), nullable=False),
    sa.Column('next_player_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['next_player_id'], ['players.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('player_id', 'session_id')
    )
    op.create_table('session_words',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('word', sa.Text(), nullable=False),
    sa.Column('proposed_by', sa.BigInteger(), nullable=False),
    sa.Column('approved', sa.Boolean(), nullable=True),
    sa.Column('previous_word', sa.BigInteger(), nullable=True),
    sa.Column('session_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['previous_word'], ['session_words.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['proposed_by'], ['players.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('votes',
    sa.Column('session_word', sa.BigInteger(), nullable=False),
    sa.Column('player_id', sa.BigInteger(), nullable=False),
    sa.Column('vote', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['session_word'], ['session_words.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('session_word', 'player_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('votes')
    op.drop_table('session_words')
    op.drop_table('association_players_sessions')
    op.drop_table('game_sessions')
    op.drop_table('players')
    op.drop_table('chats')
    op.drop_table('admins')
    # ### end Alembic commands ###
