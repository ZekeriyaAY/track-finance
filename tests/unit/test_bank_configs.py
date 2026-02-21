"""Unit tests for bank Excel-format configuration lookup."""
import pytest

from utils.bank_configs import get_bank_config, BANK_CONFIGS


@pytest.mark.unit
class TestGetBankConfig:
    """Tests for get_bank_config lookup function."""

    def test_yapikredi_config_exists(self):
        """yapikredi config is returned and has expected structure."""
        config = get_bank_config('yapikredi')
        assert config is not None
        assert config['name'] == 'Yapı Kredi'

    def test_yapikredi_has_required_keys(self):
        """yapikredi config contains columns, date_format, header_row_identifier."""
        config = get_bank_config('yapikredi')
        assert 'columns' in config
        assert 'date_format' in config
        assert 'header_row_identifier' in config
        assert 'encoding' in config

    def test_yapikredi_columns(self):
        """yapikredi columns have date, description, amount keys."""
        config = get_bank_config('yapikredi')
        columns = config['columns']
        assert 'date' in columns
        assert 'description' in columns
        assert 'amount' in columns

    def test_yapikredi_date_column_alternatives(self):
        """yapikredi date column includes 'İşlem Tarihi' and 'Tarih'."""
        config = get_bank_config('yapikredi')
        assert 'İşlem Tarihi' in config['columns']['date']
        assert 'Tarih' in config['columns']['date']

    def test_yapikredi_date_format(self):
        """yapikredi uses dd/mm/yyyy date format."""
        config = get_bank_config('yapikredi')
        assert config['date_format'] == '%d/%m/%Y'

    def test_yapikredi_skip_initial_rows(self):
        """yapikredi skips first 2 data rows."""
        config = get_bank_config('yapikredi')
        assert config['skip_initial_rows'] == 2

    def test_yapikredi_header_identifier(self):
        """yapikredi uses 'İşlem Tarihi' to find the header row."""
        config = get_bank_config('yapikredi')
        assert config['header_row_identifier'] == 'İşlem Tarihi'

    def test_kuveytturk_config_exists(self):
        """kuveytturk config is returned and has expected structure."""
        config = get_bank_config('kuveytturk')
        assert config is not None
        assert config['name'] == 'Kuveyt Türk'

    def test_kuveytturk_has_required_keys(self):
        """kuveytturk config contains columns, header_row_identifier."""
        config = get_bank_config('kuveytturk')
        assert 'columns' in config
        assert 'header_row_identifier' in config
        assert 'encoding' in config

    def test_kuveytturk_columns(self):
        """kuveytturk columns have date, description, amount keys."""
        config = get_bank_config('kuveytturk')
        columns = config['columns']
        assert 'date' in columns
        assert 'description' in columns
        assert 'amount' in columns

    def test_kuveytturk_date_format_is_none(self):
        """kuveytturk uses None date_format (Excel returns datetime objects)."""
        config = get_bank_config('kuveytturk')
        assert config['date_format'] is None

    def test_kuveytturk_skip_initial_rows_zero(self):
        """kuveytturk does not skip initial rows."""
        config = get_bank_config('kuveytturk')
        assert config['skip_initial_rows'] == 0

    def test_kuveytturk_use_bold_for_income(self):
        """kuveytturk uses bold formatting to detect income rows."""
        config = get_bank_config('kuveytturk')
        assert config['use_bold_for_income'] is True

    def test_kuveytturk_header_identifier(self):
        """kuveytturk uses 'Tarih' to find the header row."""
        config = get_bank_config('kuveytturk')
        assert config['header_row_identifier'] == 'Tarih'

    def test_unknown_bank_returns_none(self):
        """Unknown bank code returns None."""
        assert get_bank_config('nonexistent_bank') is None
        assert get_bank_config('') is None
        assert get_bank_config('garanti') is None

    def test_bank_configs_dict_has_two_entries(self):
        """BANK_CONFIGS contains exactly yapikredi and kuveytturk."""
        assert set(BANK_CONFIGS.keys()) == {'yapikredi', 'kuveytturk'}

    def test_all_configs_have_consistent_structure(self):
        """All bank configs share the same top-level keys."""
        required_keys = {'name', 'columns', 'date_format', 'header_row_identifier', 'encoding'}
        for bank_code, config in BANK_CONFIGS.items():
            for key in required_keys:
                assert key in config, \
                    f"Bank '{bank_code}' missing required key: {key}"

    def test_all_configs_columns_have_required_fields(self):
        """All bank configs have date, description, amount in columns."""
        required_fields = {'date', 'description', 'amount'}
        for bank_code, config in BANK_CONFIGS.items():
            for field in required_fields:
                assert field in config['columns'], \
                    f"Bank '{bank_code}' columns missing field: {field}"

    def test_column_alternatives_are_lists(self):
        """Column alternatives are lists of strings."""
        for bank_code, config in BANK_CONFIGS.items():
            for field, alternatives in config['columns'].items():
                assert isinstance(alternatives, list), \
                    f"Bank '{bank_code}' field '{field}' alternatives should be a list"
                for alt in alternatives:
                    assert isinstance(alt, str), \
                        f"Bank '{bank_code}' field '{field}' has non-string alternative"
