from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional


@dataclass
class BankTransaction:
    """Normalized transaction from a bank API."""
    external_id: str
    date: date
    amount: float
    type: str  # 'income' or 'expense'
    description: str
    raw_data: Optional[dict] = None


@dataclass
class BankSyncResult:
    """Result of a sync operation."""
    new_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    errors: List[str] = field(default_factory=list)
    status: str = 'success'  # 'success' / 'error' / 'partial'


class BankSyncError(Exception):
    """Raised when a bank sync operation fails."""
    pass


class BaseBankAdapter(ABC):
    """Abstract base class for bank API adapters."""

    bank_code: str = ''
    bank_name: str = ''

    def __init__(self, client_id: str, client_secret: str, account_id: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.account_id = account_id
        self.access_token: Optional[str] = None

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the bank API. Returns True on success."""
        pass

    @abstractmethod
    def fetch_transactions(self, date_from: date, date_to: date) -> List[BankTransaction]:
        """Fetch transactions within a date range."""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the connection credentials are valid."""
        pass
