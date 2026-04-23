"""Remove bank sync support

Drop bank_connection table and remove external_transaction_id,
bank_connection_id columns from cashflow_transaction.

Revision ID: 77a5c92582fe
Revises: 08f980143fd0
Create Date: 2026-04-23
"""
from alembic import op
import sqlalchemy as sa

revision = '77a5c92582fe'
down_revision = '08f980143fd0'
branch_labels = None
depends_on = None


def upgrade():
    # Drop unique constraint and index first
    op.drop_constraint('uq_external_txn_bank', 'cashflow_transaction', type_='unique')
    op.drop_index('ix_cashflow_transaction_external_transaction_id', table_name='cashflow_transaction')

    # Drop columns from cashflow_transaction
    op.drop_constraint(
        'cashflow_transaction_bank_connection_id_fkey',
        'cashflow_transaction',
        type_='foreignkey',
    )
    op.drop_column('cashflow_transaction', 'bank_connection_id')
    op.drop_column('cashflow_transaction', 'external_transaction_id')

    # Drop bank_connection table
    op.drop_table('bank_connection')


def downgrade():
    # Recreate bank_connection table
    op.create_table(
        'bank_connection',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('bank_code', sa.String(50), nullable=False),
        sa.Column('bank_name', sa.String(100), nullable=False),
        sa.Column('client_id_encrypted', sa.Text(), nullable=True),
        sa.Column('client_secret_encrypted', sa.Text(), nullable=True),
        sa.Column('account_id', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('last_sync_status', sa.String(20), nullable=True),
        sa.Column('last_sync_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # Recreate columns on cashflow_transaction
    op.add_column('cashflow_transaction', sa.Column('external_transaction_id', sa.String(255), nullable=True))
    op.add_column('cashflow_transaction', sa.Column('bank_connection_id', sa.Integer(), nullable=True))

    op.create_foreign_key(
        'cashflow_transaction_bank_connection_id_fkey',
        'cashflow_transaction', 'bank_connection',
        ['bank_connection_id'], ['id'],
    )
    op.create_index('ix_cashflow_transaction_external_transaction_id', 'cashflow_transaction', ['external_transaction_id'])
    op.create_unique_constraint('uq_external_txn_bank', 'cashflow_transaction', ['external_transaction_id', 'bank_connection_id'])
