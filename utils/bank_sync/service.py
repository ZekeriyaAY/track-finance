import logging
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta

from models import db
from models.bank_connection import BankConnection
from models.cashflow import CashflowTransaction
from models.category import Category
from models.tag import Tag
from utils.bank_sync.base import BankSyncResult, BankSyncError
from utils.bank_sync.registry import get_adapter

logger = logging.getLogger(__name__)


def sync_bank_connection(connection_id, date_from=None, date_to=None):
    """Sync transactions for a single bank connection.

    Returns a BankSyncResult with counts of new, skipped, and errored transactions.
    """
    connection = BankConnection.query.get(connection_id)
    if not connection:
        raise BankSyncError(f'Bank connection {connection_id} not found')
    if not connection.is_active:
        raise BankSyncError(f'Bank connection {connection.bank_name} is not active')

    result = BankSyncResult()

    try:
        # Get adapter and credentials
        adapter_cls = get_adapter(connection.bank_code)
        adapter = adapter_cls(
            client_id=connection.get_client_id(),
            client_secret=connection.get_client_secret(),
            account_id=connection.account_id,
        )

        # Default date range: last 3 months
        if not date_to:
            date_to = date.today()
        if not date_from:
            date_from = date_to - relativedelta(months=3)

        # Authenticate and fetch
        adapter.authenticate()
        bank_transactions = adapter.fetch_transactions(date_from, date_to)

        # Get or create "Bank Sync" category
        sync_category = Category.query.filter_by(name='Bank Sync').first()
        if not sync_category:
            sync_category = Category(name='Bank Sync')
            db.session.add(sync_category)
            db.session.flush()

        # Get or create tag for the bank
        bank_tag = Tag.query.filter_by(name=connection.bank_name).first()
        if not bank_tag:
            bank_tag = Tag(name=connection.bank_name)
            db.session.add(bank_tag)
            db.session.flush()

        # Process each transaction
        for btxn in bank_transactions:
            try:
                # Deduplication check
                existing = CashflowTransaction.query.filter_by(
                    external_transaction_id=btxn.external_id,
                    bank_connection_id=connection.id,
                ).first()

                if existing:
                    result.skipped_count += 1
                    continue

                txn = CashflowTransaction(
                    date=btxn.date,
                    amount=btxn.amount,
                    type=btxn.type,
                    description=btxn.description,
                    category_id=sync_category.id,
                    source='bank_sync',
                    external_transaction_id=btxn.external_id,
                    bank_connection_id=connection.id,
                    tags=[bank_tag],
                )
                db.session.add(txn)
                result.new_count += 1

            except Exception as e:
                logger.error(f'Error processing bank transaction {btxn.external_id}: {e}')
                result.error_count += 1
                result.errors.append(str(e))

        db.session.commit()

        # Update connection sync status
        connection.last_sync_at = datetime.now(timezone.utc)
        if result.error_count > 0 and result.new_count > 0:
            connection.last_sync_status = 'partial'
            result.status = 'partial'
        elif result.error_count > 0:
            connection.last_sync_status = 'error'
            result.status = 'error'
        else:
            connection.last_sync_status = 'success'
            result.status = 'success'

        connection.last_sync_message = (
            f'{result.new_count} new, {result.skipped_count} skipped, {result.error_count} errors'
        )
        db.session.commit()

    except BankSyncError as e:
        connection.last_sync_at = datetime.now(timezone.utc)
        connection.last_sync_status = 'error'
        connection.last_sync_message = str(e)
        db.session.commit()
        result.status = 'error'
        result.errors.append(str(e))

    return result
