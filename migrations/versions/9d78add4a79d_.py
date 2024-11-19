"""empty message

Revision ID: 9d78add4a79d
Revises: 73a2aab6796f
Create Date: 2024-10-26 15:00:26.878678

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9d78add4a79d'
down_revision = '73a2aab6796f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('race_dates', schema=None) as batch_op:
        batch_op.alter_column('expires_at',
               existing_type=sa.DATE(),
               nullable=False)

    with op.batch_alter_table('race_result', schema=None) as batch_op:
        batch_op.add_column(sa.Column('race_title', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('predict_flag', sa.Boolean(), nullable=False))
        batch_op.drop_column('predict_frag')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('race_result', schema=None) as batch_op:
        batch_op.add_column(sa.Column('predict_frag', mysql.TINYINT(display_width=1), autoincrement=False, nullable=False))
        batch_op.drop_column('predict_flag')
        batch_op.drop_column('race_title')

    with op.batch_alter_table('race_dates', schema=None) as batch_op:
        batch_op.alter_column('expires_at',
               existing_type=sa.DATE(),
               nullable=True)

    # ### end Alembic commands ###
