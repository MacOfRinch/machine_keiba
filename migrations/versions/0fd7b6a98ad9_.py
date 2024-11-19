"""empty message

Revision ID: 0fd7b6a98ad9
Revises: 13e8c91d98a0
Create Date: 2024-11-04 11:30:53.312261

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fd7b6a98ad9'
down_revision = '13e8c91d98a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('race_result', schema=None) as batch_op:
        batch_op.add_column(sa.Column('horse_number', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('race_result', schema=None) as batch_op:
        batch_op.drop_column('horse_number')

    # ### end Alembic commands ###