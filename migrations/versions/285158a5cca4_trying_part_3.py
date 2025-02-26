"""trying part 3 

Revision ID: 285158a5cca4
Revises: 5c7f2a8fc78c
Create Date: 2025-02-24 19:50:44.890984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '285158a5cca4'
down_revision = '5c7f2a8fc78c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('billings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('amount', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('package_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'package', ['package_id'], ['id'])
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('billings', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')
        batch_op.drop_column('package_id')
        batch_op.drop_column('amount')

    # ### end Alembic commands ###
