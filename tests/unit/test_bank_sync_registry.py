"""Unit tests for the bank sync adapter registry."""
import pytest

from utils.bank_sync.registry import (
    _adapter_registry,
    register_adapter,
    get_adapter,
    get_available_banks,
)
from utils.bank_sync.base import BaseBankAdapter


@pytest.mark.unit
class TestAdapterRegistry:
    """Tests for adapter registration, lookup, and listing."""

    @pytest.fixture(autouse=True)
    def clean_registry(self):
        """Save and restore the global registry around each test."""
        saved = dict(_adapter_registry)
        _adapter_registry.clear()
        yield
        _adapter_registry.clear()
        _adapter_registry.update(saved)

    # -- Registration via decorator ------------------------------------------

    def test_register_adapter_decorator(self):
        """@register_adapter adds the class to the registry."""

        @register_adapter
        class FakeAdapter(BaseBankAdapter):
            bank_code = 'fake'
            bank_name = 'Fake Bank'

            def authenticate(self):
                return True

            def fetch_transactions(self, date_from, date_to):
                return []

            def test_connection(self):
                return True

        assert 'fake' in _adapter_registry
        assert _adapter_registry['fake'] is FakeAdapter

    def test_register_adapter_returns_class(self):
        """The decorator returns the class itself (transparent)."""

        @register_adapter
        class TransparentAdapter(BaseBankAdapter):
            bank_code = 'transparent'
            bank_name = 'Transparent'

            def authenticate(self):
                return True

            def fetch_transactions(self, date_from, date_to):
                return []

            def test_connection(self):
                return True

        assert TransparentAdapter.bank_code == 'transparent'

    def test_register_multiple_adapters(self):
        """Multiple adapters can be registered with different codes."""

        @register_adapter
        class AdapterA(BaseBankAdapter):
            bank_code = 'bank_a'
            bank_name = 'Bank A'

            def authenticate(self):
                return True

            def fetch_transactions(self, date_from, date_to):
                return []

            def test_connection(self):
                return True

        @register_adapter
        class AdapterB(BaseBankAdapter):
            bank_code = 'bank_b'
            bank_name = 'Bank B'

            def authenticate(self):
                return True

            def fetch_transactions(self, date_from, date_to):
                return []

            def test_connection(self):
                return True

        assert len(_adapter_registry) == 2
        assert 'bank_a' in _adapter_registry
        assert 'bank_b' in _adapter_registry

    def test_register_overwrites_same_code(self):
        """Re-registering the same bank_code overwrites the previous adapter."""

        @register_adapter
        class OldAdapter(BaseBankAdapter):
            bank_code = 'dup'
            bank_name = 'Old'

            def authenticate(self):
                return True

            def fetch_transactions(self, date_from, date_to):
                return []

            def test_connection(self):
                return True

        @register_adapter
        class NewAdapter(BaseBankAdapter):
            bank_code = 'dup'
            bank_name = 'New'

            def authenticate(self):
                return True

            def fetch_transactions(self, date_from, date_to):
                return []

            def test_connection(self):
                return True

        assert _adapter_registry['dup'] is NewAdapter
        assert len(_adapter_registry) == 1

    # -- Lookup via get_adapter -----------------------------------------------

    def test_get_adapter_returns_class(self):
        """get_adapter returns the registered adapter class."""

        @register_adapter
        class LookupAdapter(BaseBankAdapter):
            bank_code = 'lookup'
            bank_name = 'Lookup Bank'

            def authenticate(self):
                return True

            def fetch_transactions(self, date_from, date_to):
                return []

            def test_connection(self):
                return True

        cls = get_adapter('lookup')
        assert cls is LookupAdapter

    def test_get_adapter_unknown_raises_valueerror(self):
        """get_adapter raises ValueError for an unregistered bank_code."""
        with pytest.raises(ValueError, match='No adapter registered'):
            get_adapter('nonexistent')

    def test_get_adapter_empty_string_raises(self):
        """get_adapter with empty string raises ValueError."""
        with pytest.raises(ValueError, match='No adapter registered'):
            get_adapter('')

    # -- Listing via get_available_banks --------------------------------------

    def test_get_available_banks_empty(self):
        """get_available_banks returns empty list when nothing is registered."""
        result = get_available_banks()
        assert result == []

    def test_get_available_banks_returns_tuples(self):
        """get_available_banks returns (bank_code, bank_name) tuples."""

        @register_adapter
        class TupleAdapter(BaseBankAdapter):
            bank_code = 'tuple_bank'
            bank_name = 'Tuple Bank'

            def authenticate(self):
                return True

            def fetch_transactions(self, date_from, date_to):
                return []

            def test_connection(self):
                return True

        banks = get_available_banks()
        assert len(banks) == 1
        code, name = banks[0]
        assert code == 'tuple_bank'
        assert name == 'Tuple Bank'

    def test_get_available_banks_multiple(self):
        """get_available_banks lists all registered adapters."""

        @register_adapter
        class BankX(BaseBankAdapter):
            bank_code = 'x'
            bank_name = 'Bank X'

            def authenticate(self):
                return True

            def fetch_transactions(self, date_from, date_to):
                return []

            def test_connection(self):
                return True

        @register_adapter
        class BankY(BaseBankAdapter):
            bank_code = 'y'
            bank_name = 'Bank Y'

            def authenticate(self):
                return True

            def fetch_transactions(self, date_from, date_to):
                return []

            def test_connection(self):
                return True

        banks = get_available_banks()
        codes = [b[0] for b in banks]
        names = [b[1] for b in banks]

        assert 'x' in codes
        assert 'y' in codes
        assert 'Bank X' in names
        assert 'Bank Y' in names


@pytest.mark.unit
class TestBaseBankAdapterDataclasses:
    """Tests for the dataclasses and exception in base.py."""

    def test_bank_transaction_dataclass(self):
        """BankTransaction dataclass stores fields correctly."""
        from datetime import date as d
        from utils.bank_sync.base import BankTransaction

        bt = BankTransaction(
            external_id='EXT-001',
            date=d(2024, 1, 15),
            amount=500.0,
            type='income',
            description='Salary deposit',
        )
        assert bt.external_id == 'EXT-001'
        assert bt.amount == 500.0
        assert bt.type == 'income'
        assert bt.raw_data is None

    def test_bank_transaction_with_raw_data(self):
        """BankTransaction can carry raw_data dict."""
        from datetime import date as d
        from utils.bank_sync.base import BankTransaction

        raw = {'ref': 'ABC123', 'extra': True}
        bt = BankTransaction(
            external_id='EXT-002', date=d(2024, 2, 1),
            amount=100.0, type='expense', description='test',
            raw_data=raw,
        )
        assert bt.raw_data == raw

    def test_bank_sync_result_defaults(self):
        """BankSyncResult default values are zero/empty."""
        from utils.bank_sync.base import BankSyncResult

        r = BankSyncResult()
        assert r.new_count == 0
        assert r.skipped_count == 0
        assert r.error_count == 0
        assert r.errors == []
        assert r.status == 'success'

    def test_bank_sync_result_mutable(self):
        """BankSyncResult fields can be mutated."""
        from utils.bank_sync.base import BankSyncResult

        r = BankSyncResult()
        r.new_count = 5
        r.skipped_count = 2
        r.error_count = 1
        r.errors.append('some error')
        r.status = 'partial'

        assert r.new_count == 5
        assert r.status == 'partial'
        assert len(r.errors) == 1

    def test_bank_sync_error_exception(self):
        """BankSyncError is an Exception with a message."""
        from utils.bank_sync.base import BankSyncError

        err = BankSyncError('connection failed')
        assert str(err) == 'connection failed'
        assert isinstance(err, Exception)

    def test_base_bank_adapter_is_abstract(self):
        """BaseBankAdapter cannot be instantiated directly (abstract methods)."""
        with pytest.raises(TypeError):
            BaseBankAdapter('id', 'secret')

    def test_concrete_adapter_instantiation(self):
        """A fully implemented adapter can be instantiated."""

        class ConcreteAdapter(BaseBankAdapter):
            bank_code = 'concrete'
            bank_name = 'Concrete'

            def authenticate(self):
                return True

            def fetch_transactions(self, date_from, date_to):
                return []

            def test_connection(self):
                return True

        adapter = ConcreteAdapter('cid', 'csecret', 'acc123')
        assert adapter.client_id == 'cid'
        assert adapter.client_secret == 'csecret'
        assert adapter.account_id == 'acc123'
        assert adapter.access_token is None
