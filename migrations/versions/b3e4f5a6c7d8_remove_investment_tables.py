"""Remove investment tables

Drop investment_transaction and investment_type tables.

Revision ID: b3e4f5a6c7d8
Revises: 77a5c92582fe
Create Date: 2026-04-23
"""
from alembic import op
import sqlalchemy as sa

revision = 'b3e4f5a6c7d8'
down_revision = '77a5c92582fe'
branch_labels = None
depends_on = None


def upgrade():
    # Drop child table first (has FK to investment_type)
    op.drop_table('investment_transaction')
    op.drop_table('investment_type')


def downgrade():
    # Recreate investment_type table
    op.create_table(
        'investment_type',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('icon', sa.String(50), server_default='fas fa-chart-pie'),
        sa.Column('color', sa.String(7), server_default='#3B82F6'),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('investment_type.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Recreate investment_transaction table
    op.create_table(
        'investment_transaction',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('investment_type_id', sa.Integer(), sa.ForeignKey('investment_type.id'), nullable=False),
        sa.Column('transaction_date', sa.DateTime(), nullable=False),
        sa.Column('transaction_type', sa.String(10), nullable=False),
        sa.Column('price', sa.Numeric(12, 2), nullable=False),
        sa.Column('quantity', sa.Numeric(15, 6), nullable=False),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
