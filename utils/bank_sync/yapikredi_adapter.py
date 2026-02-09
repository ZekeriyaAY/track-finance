import logging
from datetime import date
from typing import List

import requests

from utils.bank_sync.base import BaseBankAdapter, BankTransaction, BankSyncError
from utils.bank_sync.registry import register_adapter

logger = logging.getLogger(__name__)

TOKEN_URL = 'https://api.yapikredi.com.tr/auth/oauth/v2/token'
TRANSACTIONS_URL = 'https://api.yapikredi.com.tr/api/accounts/{account_id}/transactions'


@register_adapter
class YapiKrediAdapter(BaseBankAdapter):
    bank_code = 'yapikredi'
    bank_name = 'Yapı Kredi'

    def authenticate(self) -> bool:
        """OAuth2 client_credentials flow."""
        try:
            resp = requests.post(TOKEN_URL, data={
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'accounts transactions',
            }, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            self.access_token = data.get('access_token')
            if not self.access_token:
                raise BankSyncError('No access_token in response')
            return True
        except requests.RequestException as e:
            logger.error(f'Yapı Kredi auth failed: {e}')
            raise BankSyncError(f'Authentication failed: {e}')

    def fetch_transactions(self, date_from: date, date_to: date) -> List[BankTransaction]:
        """Fetch transactions from Yapı Kredi API."""
        if not self.access_token:
            self.authenticate()

        account_id = self.account_id or 'default'
        url = TRANSACTIONS_URL.format(account_id=account_id)
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
        params = {
            'dateFrom': date_from.isoformat(),
            'dateTo': date_to.isoformat(),
        }

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=30)

            # Re-auth on 401
            if resp.status_code == 401:
                logger.info('Token expired, re-authenticating...')
                self.authenticate()
                headers['Authorization'] = f'Bearer {self.access_token}'
                resp = requests.get(url, headers=headers, params=params, timeout=30)

            resp.raise_for_status()
            return self._parse_transactions(resp.json())
        except requests.RequestException as e:
            logger.error(f'Yapı Kredi fetch failed: {e}')
            raise BankSyncError(f'Failed to fetch transactions: {e}')

    def _parse_transactions(self, data: dict) -> List[BankTransaction]:
        """Parse Yapı Kredi API response into BankTransaction list.

        NOTE: The actual response format depends on Yapı Kredi API documentation.
        This is a placeholder implementation that should be adjusted based on
        the real API response structure.
        """
        transactions = []
        items = data.get('transactions', data.get('data', []))

        for item in items:
            try:
                amount = float(item.get('amount', 0))
                txn_type = 'income' if amount >= 0 else 'expense'

                txn_date_str = item.get('date', item.get('transactionDate', ''))
                if txn_date_str:
                    txn_date = date.fromisoformat(txn_date_str[:10])
                else:
                    continue

                transactions.append(BankTransaction(
                    external_id=str(item.get('id', item.get('transactionId', ''))),
                    date=txn_date,
                    amount=abs(amount),
                    type=txn_type,
                    description=item.get('description', item.get('merchantName', '')),
                    raw_data=item,
                ))
            except (ValueError, KeyError) as e:
                logger.warning(f'Skipping unparseable transaction: {e}')
                continue

        return transactions

    def test_connection(self) -> bool:
        """Test connection by authenticating."""
        try:
            self.authenticate()
            return True
        except BankSyncError:
            return False
