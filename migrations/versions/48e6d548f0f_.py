"""empty message

Revision ID: 48e6d548f0f
Revises: 7670a05866
Create Date: 2015-11-07 14:03:03.505241

"""

# revision identifiers, used by Alembic.
revision = '48e6d548f0f'
down_revision = '7670a05866'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('statements', sa.Column('topic_id', sa.Integer(), nullable=False))
    op.drop_constraint('statements_event_id_fkey', 'statements', type_='foreignkey')
    op.create_foreign_key(None, 'statements', 'topics', ['topic_id'], ['id'])
    op.drop_column('statements', 'event_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('statements', sa.Column('event_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'statements', type_='foreignkey')
    op.create_foreign_key('statements_event_id_fkey', 'statements', 'events', ['event_id'], ['id'])
    op.drop_column('statements', 'topic_id')
    ### end Alembic commands ###