"""amount float to numeric

Revision ID: a1b2c3d4e5f6
Revises: 31087fde7665
Create Date: 2026-02-22 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '31087fde7665'
branch_labels = None
depends_on = None


def upgrade():
    # CashflowTransaction: amount Float -> Numeric(12, 2)
    op.alter_column('cashflow_transaction', 'amount',
                    existing_type=sa.Float(),
                    type_=sa.Numeric(precision=12, scale=2),
                    existing_nullable=False)

    # InvestmentTransaction: price Float -> Numeric(12, 2)
    op.alter_column('investment_transaction', 'price',
                    existing_type=sa.Float(),
                    type_=sa.Numeric(precision=12, scale=2),
                    existing_nullable=False)

    # InvestmentTransaction: quantity Float -> Numeric(15, 6)
    op.alter_column('investment_transaction', 'quantity',
                    existing_type=sa.Float(),
                    type_=sa.Numeric(precision=15, scale=6),
                    existing_nullable=False)

    # InvestmentTransaction: total_amount Float -> Numeric(12, 2)
    op.alter_column('investment_transaction', 'total_amount',
                    existing_type=sa.Float(),
                    type_=sa.Numeric(precision=12, scale=2),
                    existing_nullable=False)


def downgrade():
    op.alter_column('investment_transaction', 'total_amount',
                    existing_type=sa.Numeric(precision=12, scale=2),
                    type_=sa.Float(),
                    existing_nullable=False)

    op.alter_column('investment_transaction', 'quantity',
                    existing_type=sa.Numeric(precision=15, scale=6),
                    type_=sa.Float(),
                    existing_nullable=False)

    op.alter_column('investment_transaction', 'price',
                    existing_type=sa.Numeric(precision=12, scale=2),
                    type_=sa.Float(),
                    existing_nullable=False)

    op.alter_column('cashflow_transaction', 'amount',
                    existing_type=sa.Numeric(precision=12, scale=2),
                    type_=sa.Float(),
                    existing_nullable=False)
