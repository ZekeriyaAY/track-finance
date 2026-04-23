"""Add database indexes for frequently queried columns

Revision ID: c4d5e6f7a8b9
Revises: b3e4f5a6c7d8
Create Date: 2026-04-24
"""
from alembic import op

revision = 'c4d5e6f7a8b9'
down_revision = 'b3e4f5a6c7d8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_cashflow_transaction_date', 'cashflow_transaction', ['date'])
    op.create_index('ix_cashflow_transaction_category_id', 'cashflow_transaction', ['category_id'])
    op.create_index('ix_cashflow_transaction_type', 'cashflow_transaction', ['type'])
    op.create_index('ix_category_parent_id', 'category', ['parent_id'])
    op.create_index('ix_categorization_rule_active_priority', 'categorization_rule', ['is_active', 'priority'])
    op.create_index('ix_cashflow_transaction_tags_tag_id', 'cashflow_transaction_tags', ['tag_id'])


def downgrade():
    op.drop_index('ix_cashflow_transaction_tags_tag_id', table_name='cashflow_transaction_tags')
    op.drop_index('ix_categorization_rule_active_priority', table_name='categorization_rule')
    op.drop_index('ix_category_parent_id', table_name='category')
    op.drop_index('ix_cashflow_transaction_type', table_name='cashflow_transaction')
    op.drop_index('ix_cashflow_transaction_category_id', table_name='cashflow_transaction')
    op.drop_index('ix_cashflow_transaction_date', table_name='cashflow_transaction')
