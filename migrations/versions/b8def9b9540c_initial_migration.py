"""initial migration

Revision ID: b8def9b9540c
Revises: 
Create Date: 2025-02-24 12:47:51.147929

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8def9b9540c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('agency',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('agency_name', sa.String(), nullable=False),
    sa.Column('agency_email', sa.String(), nullable=False),
    sa.Column('agency_phone_number', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('agency_password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('agency_email')
    )
    op.create_table('billings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('checkoutID', sa.BigInteger(), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=False),
    sa.Column('response_description', sa.Text(), nullable=True),
    sa.Column('customer_message', sa.Text(), nullable=True),
    sa.Column('payment_status', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=False),
    sa.Column('gender', sa.String(length=10), nullable=False),
    sa.Column('image_url', sa.String(length=200), nullable=True),
    sa.Column('password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('package',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('package_name', sa.String(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('location', sa.String(), nullable=False),
    sa.Column('day_count', sa.Integer(), nullable=False),
    sa.Column('package_type', sa.String(), nullable=False),
    sa.Column('inclusions', sa.Text(), nullable=False),
    sa.Column('exclusions', sa.Text(), nullable=False),
    sa.Column('agency_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['agency_id'], ['agency.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bookings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('package_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('billing_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['billing_id'], ['billings.id'], ),
    sa.ForeignKeyConstraint(['package_id'], ['package.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('photos',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('package_id', sa.Integer(), nullable=False),
    sa.Column('photo_url', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['package_id'], ['package.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reviews',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('package_id', sa.Integer(), nullable=False),
    sa.Column('image', sa.String(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('review_texts', sa.Text(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['package_id'], ['package.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reviews')
    op.drop_table('photos')
    op.drop_table('bookings')
    op.drop_table('package')
    op.drop_table('user')
    op.drop_table('billings')
    op.drop_table('agency')
    # ### end Alembic commands ###
