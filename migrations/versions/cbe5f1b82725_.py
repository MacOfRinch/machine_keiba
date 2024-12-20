"""empty message

Revision ID: cbe5f1b82725
Revises: 0fd7b6a98ad9
Create Date: 2024-11-04 12:21:27.351066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cbe5f1b82725'
down_revision = '0fd7b6a98ad9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('race_result', schema=None) as batch_op:
        batch_op.add_column(sa.Column('box_number', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('race_result', schema=None) as batch_op:
        batch_op.drop_column('box_number')

    # ### end Alembic commands ###
