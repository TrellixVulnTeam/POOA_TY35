"""Add session_id

Revision ID: d8fa5dd60412
Revises: 6ce4d32d1e69
Create Date: 2019-10-22 15:49:40.504503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8fa5dd60412'
down_revision = '6ce4d32d1e69'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('session_id', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'session_id')
    # ### end Alembic commands ###