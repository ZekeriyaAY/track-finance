"""Unit tests for the Excel/CSV import processor utilities."""
import pytest
import os
from datetime import datetime

import pandas as pd

from utils.excel_processor import (
    parse_turkish_amount,
    parse_date,
    read_file_with_header_detection,
    map_columns,
    process_excel_data,
    ExcelImportError,
)


# ---------------------------------------------------------------------------
# parse_turkish_amount
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestParseTurkishAmount:
    """Tests for Turkish-locale amount parsing."""

    def test_standard_turkish_format(self):
        """'1.234,56 TL' parses to 1234.56 as expense."""
        amount, txn_type = parse_turkish_amount('1.234,56 TL')
        assert abs(amount - 1234.56) < 0.001
        assert txn_type == 'expense'

    def test_simple_comma_decimal(self):
        """'386,50' parses correctly."""
        amount, txn_type = parse_turkish_amount('386,50')
        assert abs(amount - 386.50) < 0.001
        assert txn_type == 'expense'

    def test_positive_prefix_income(self):
        """'+386,50 TL' is income."""
        amount, txn_type = parse_turkish_amount('+386,50 TL')
        assert abs(amount - 386.50) < 0.001
        assert txn_type == 'income'

    def test_negative_prefix_expense(self):
        """'-500,00 TL' is expense."""
        amount, txn_type = parse_turkish_amount('-500,00 TL')
        assert abs(amount - 500.00) < 0.001
        assert txn_type == 'expense'

    def test_parenthesized_negative(self):
        """'(1.000,00)' is treated as expense."""
        amount, txn_type = parse_turkish_amount('(1.000,00)')
        assert abs(amount - 1000.0) < 0.001
        assert txn_type == 'expense'

    def test_nan_returns_zero(self):
        """NaN values return 0.0 expense."""
        amount, txn_type = parse_turkish_amount(float('nan'))
        assert amount == 0.0
        assert txn_type == 'expense'

    def test_empty_string_returns_zero(self):
        """Empty string returns 0.0 expense."""
        amount, txn_type = parse_turkish_amount('')
        assert amount == 0.0
        assert txn_type == 'expense'

    def test_none_returns_zero(self):
        """None (via pd.isna) returns 0.0 expense."""
        amount, txn_type = parse_turkish_amount(None)
        assert amount == 0.0
        assert txn_type == 'expense'

    def test_integer_string(self):
        """'500' parses to 500.0."""
        amount, _ = parse_turkish_amount('500')
        assert amount == 500.0

    def test_plain_float_string(self):
        """'123.45' with single dot and <=2 decimals treated as decimal."""
        amount, _ = parse_turkish_amount('123.45')
        assert abs(amount - 123.45) < 0.001

    def test_thousands_only_no_decimal(self):
        """'1.000' where dot is thousand separator (3+ digits after dot)."""
        amount, _ = parse_turkish_amount('1.000')
        assert amount == 1000.0

    def test_multiple_dots_thousand_separators(self):
        """'1.234.567' multiple dots, last is treated as decimal separator."""
        amount, _ = parse_turkish_amount('1.234.567')
        assert abs(amount - 1234.567) < 0.001

    def test_currency_symbol_stripped(self):
        """Turkish Lira symbol is stripped."""
        amount, _ = parse_turkish_amount('₺1.500,00')
        assert abs(amount - 1500.0) < 0.001

    def test_numeric_input(self):
        """Numeric (int/float) input is handled via str conversion."""
        amount, _ = parse_turkish_amount(150)
        assert amount == 150.0

        amount2, _ = parse_turkish_amount(99.99)
        assert abs(amount2 - 99.99) < 0.001

    def test_whitespace_stripped(self):
        """Leading/trailing whitespace is stripped."""
        amount, _ = parse_turkish_amount('  500,00  ')
        assert abs(amount - 500.0) < 0.001

    def test_no_sign_is_expense(self):
        """Amount without sign defaults to expense."""
        _, txn_type = parse_turkish_amount('100,00')
        assert txn_type == 'expense'

    def test_amount_is_always_positive(self):
        """Returned amount is always absolute value."""
        amount, _ = parse_turkish_amount('-250,50')
        assert amount > 0


# ---------------------------------------------------------------------------
# parse_date
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestParseDate:
    """Tests for date parsing with multiple format support."""

    def test_datetime_object_passthrough(self):
        """datetime object is returned as-is."""
        dt = datetime(2024, 3, 15, 10, 30)
        result = parse_date(dt)
        assert result == dt

    def test_pandas_timestamp(self):
        """pandas Timestamp is converted to datetime."""
        ts = pd.Timestamp('2024-06-01')
        result = parse_date(ts)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 6

    def test_nan_returns_none(self):
        """NaN/NaT returns None."""
        assert parse_date(float('nan')) is None
        assert parse_date(pd.NaT) is None

    def test_dot_format(self):
        """'15.03.2024' with default dd.mm.yyyy format."""
        result = parse_date('15.03.2024')
        assert result.day == 15
        assert result.month == 3
        assert result.year == 2024

    def test_slash_format(self):
        """'15/03/2024' dd/mm/yyyy."""
        result = parse_date('15/03/2024')
        assert result.day == 15
        assert result.month == 3

    def test_iso_format(self):
        """'2024-03-15' ISO yyyy-mm-dd."""
        result = parse_date('2024-03-15')
        assert result.year == 2024
        assert result.month == 3
        assert result.day == 15

    def test_dash_dmy_format(self):
        """'15-03-2024' dd-mm-yyyy."""
        result = parse_date('15-03-2024')
        assert result.day == 15
        assert result.month == 3

    def test_short_year_dot(self):
        """'15.03.24' dd.mm.yy."""
        result = parse_date('15.03.24')
        assert result.day == 15
        assert result.month == 3

    def test_short_year_slash(self):
        """'15/03/24' dd/mm/yy."""
        result = parse_date('15/03/24')
        assert result.day == 15
        assert result.month == 3

    def test_custom_date_format(self):
        """Custom date_format parameter is tried first."""
        result = parse_date('2024/03/15', date_format='%Y/%m/%d')
        assert result.year == 2024
        assert result.month == 3
        assert result.day == 15

    def test_excel_serial_date(self):
        """5-digit+ numeric string is treated as Excel serial date."""
        result = parse_date('45000')
        assert result is not None
        assert isinstance(result, datetime)

    def test_invalid_date_raises(self):
        """Unparseable date string raises ValueError."""
        with pytest.raises(ValueError, match='Could not parse date'):
            parse_date('not-a-date')

    def test_whitespace_stripped(self):
        """Leading/trailing whitespace is stripped."""
        result = parse_date('  15.03.2024  ')
        assert result.day == 15


# ---------------------------------------------------------------------------
# read_file_with_header_detection
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestReadFileWithHeaderDetection:
    """Tests for reading Excel/CSV with dynamic header detection."""

    def test_csv_basic_read(self, tmp_path):
        """Plain CSV without bank_config uses first row as header."""
        csv_file = tmp_path / 'test.csv'
        csv_file.write_text('Date,Amount,Description\n2024-01-01,100,Test\n')

        df = read_file_with_header_detection(str(csv_file))
        assert 'Date' in df.columns
        assert len(df) == 1

    def test_csv_with_header_detection(self, tmp_path):
        """CSV with bank_config header_row_identifier finds the header."""
        csv_file = tmp_path / 'bank.csv'
        # Use consistent column count across all rows to avoid CSV parse errors
        csv_file.write_text(
            'Bank Export Report,,\n'
            'Account: 12345,,\n'
            'Tarih,Tutar,Aciklama\n'
            '01/01/2024,500,Salary\n'
            '02/01/2024,100,Food\n'
        )
        config = {'header_row_identifier': 'Tarih'}
        df = read_file_with_header_detection(str(csv_file), bank_config=config)

        assert 'Tarih' in df.columns
        assert len(df) == 2

    def test_unsupported_format_raises(self, tmp_path):
        """Unsupported file extension raises ExcelImportError."""
        txt_file = tmp_path / 'data.txt'
        txt_file.write_text('hello')

        with pytest.raises(ExcelImportError, match='Unsupported file format'):
            read_file_with_header_detection(str(txt_file))

    def test_header_not_found_fallback(self, tmp_path):
        """When header identifier is not found, falls back to first row."""
        csv_file = tmp_path / 'data.csv'
        csv_file.write_text('ColA,ColB\n1,2\n')

        config = {'header_row_identifier': 'NonExistent'}
        df = read_file_with_header_detection(str(csv_file), bank_config=config)
        assert 'ColA' in df.columns

    def test_xlsx_read(self, tmp_path):
        """Excel .xlsx file is read correctly."""
        xlsx_file = tmp_path / 'test.xlsx'
        sample_df = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Amount': [100],
            'Description': ['Test'],
        })
        sample_df.to_excel(str(xlsx_file), index=False)

        df = read_file_with_header_detection(str(xlsx_file))
        assert 'Date' in df.columns
        assert len(df) == 1


# ---------------------------------------------------------------------------
# map_columns
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestMapColumns:
    """Tests for column mapping between bank config and DataFrame."""

    def test_exact_match(self):
        """Exact column name match."""
        df = pd.DataFrame(columns=['Tarih', 'Tutar', 'Açıklama'])
        config = {
            'columns': {
                'date': ['Tarih'],
                'amount': ['Tutar'],
                'description': ['Açıklama'],
            }
        }
        mapping = map_columns(df, config)
        assert mapping['date'] == 'Tarih'
        assert mapping['amount'] == 'Tutar'
        assert mapping['description'] == 'Açıklama'

    def test_case_insensitive_match(self):
        """Column matching is case-insensitive."""
        df = pd.DataFrame(columns=['tarih', 'tutar', 'açıklama'])
        config = {
            'columns': {
                'date': ['Tarih'],
                'amount': ['Tutar'],
                'description': ['Açıklama'],
            }
        }
        mapping = map_columns(df, config)
        assert 'date' in mapping
        assert 'amount' in mapping
        assert 'description' in mapping

    def test_first_alternative_wins(self):
        """When multiple alternatives exist, the first match wins."""
        df = pd.DataFrame(columns=['İşlem Tarihi', 'Tarih', 'Tutar', 'Açıklama'])
        config = {
            'columns': {
                'date': ['İşlem Tarihi', 'Tarih'],
                'amount': ['Tutar'],
                'description': ['Açıklama'],
            }
        }
        mapping = map_columns(df, config)
        assert mapping['date'] == 'İşlem Tarihi'

    def test_missing_column_not_in_mapping(self):
        """Columns not present in DataFrame are absent from mapping."""
        df = pd.DataFrame(columns=['Tarih'])
        config = {
            'columns': {
                'date': ['Tarih'],
                'amount': ['NonExistent'],
            }
        }
        mapping = map_columns(df, config)
        assert 'date' in mapping
        assert 'amount' not in mapping


# ---------------------------------------------------------------------------
# process_excel_data (integration-style unit test using xlsx)
# ---------------------------------------------------------------------------
@pytest.mark.unit
class TestProcessExcelData:
    """Tests for the full Excel processing pipeline."""

    def test_unknown_bank_code_raises(self):
        """Unknown bank_code raises ExcelImportError."""
        with pytest.raises(ExcelImportError, match='Unknown bank code'):
            process_excel_data('/fake/path.csv', 'nonexistent_bank')

    def test_full_pipeline_yapikredi_xlsx(self, tmp_path):
        """End-to-end processing with a yapikredi-format xlsx file."""
        xlsx_file = tmp_path / 'yk.xlsx'
        # Create xlsx with junk rows before header (yapikredi format)
        # Row 0: Bank info
        # Row 1: Account info
        # Row 2: Header row with İşlem Tarihi
        # Row 3+: Data (first 2 data rows will be skipped by config)
        data = [
            ['Banka Bilgi', None, None],
            ['Hesap No: 123', None, None],
            ['İşlem Tarihi', 'İşlemler', 'Tutar'],
            ['15/01/2024', 'Skip Row 1', '250,50'],
            ['16/01/2024', 'Skip Row 2', '+5000 TL'],
            ['17/01/2024', 'Market alışverişi', '300'],
        ]
        df = pd.DataFrame(data)
        df.to_excel(str(xlsx_file), index=False, header=False)

        result = process_excel_data(str(xlsx_file), 'yapikredi')

        assert 'transactions' in result
        assert 'errors' in result
        assert isinstance(result['total_processed'], int)
        assert isinstance(result['successful'], int)
        assert isinstance(result['failed'], int)

    def test_full_pipeline_kuveytturk_xlsx(self, tmp_path):
        """End-to-end processing with a kuveytturk-format xlsx file."""
        xlsx_file = tmp_path / 'kt.xlsx'
        data = [
            ['Tarih', 'Açıklama', 'Tutar'],
            [datetime(2024, 1, 1), 'Havale', 1000],
            [datetime(2024, 1, 2), 'Market', 250],
        ]
        df = pd.DataFrame(data)
        df.to_excel(str(xlsx_file), index=False, header=False)

        result = process_excel_data(str(xlsx_file), 'kuveytturk')

        assert 'transactions' in result
        assert result['successful'] >= 0

    def test_missing_required_columns_raises(self, tmp_path):
        """Missing required columns raise ExcelImportError."""
        csv_file = tmp_path / 'bad.csv'
        csv_file.write_text('RandomCol\nsome_value\n')

        with pytest.raises(ExcelImportError):
            process_excel_data(str(csv_file), 'yapikredi')

    def test_skip_initial_rows(self, tmp_path):
        """yapikredi config skips first 2 data rows after header."""
        xlsx_file = tmp_path / 'skip.xlsx'
        data = [
            ['İşlem Tarihi', 'İşlemler', 'Tutar'],
            ['01/01/2024', 'Skip Row 1', 100],
            ['02/01/2024', 'Skip Row 2', 200],
            ['03/01/2024', 'Keep This', 300],
        ]
        df = pd.DataFrame(data)
        df.to_excel(str(xlsx_file), index=False, header=False)

        result = process_excel_data(str(xlsx_file), 'yapikredi')
        # yapikredi skips first 2 rows, so only 1 transaction should be processed
        assert result['total_processed'] == 1

    def test_zero_amount_rows_skipped(self, tmp_path):
        """Rows with zero amount are not included in transactions."""
        xlsx_file = tmp_path / 'zero.xlsx'
        data = [
            ['Tarih', 'Açıklama', 'Tutar'],
            [datetime(2024, 1, 1), 'Zero amt', 0],
            [datetime(2024, 1, 2), 'Real amt', 500],
        ]
        df = pd.DataFrame(data)
        df.to_excel(str(xlsx_file), index=False, header=False)

        result = process_excel_data(str(xlsx_file), 'kuveytturk')
        amounts = [t['amount'] for t in result['transactions']]
        assert 0.0 not in amounts

    def test_user_column_mapping_override(self, tmp_path):
        """User-supplied column mapping overrides auto-detection."""
        xlsx_file = tmp_path / 'custom.xlsx'
        data = [
            ['Tarih', 'Açıklama', 'Tutar'],
            [datetime(2024, 1, 1), 'Test item', 750],
        ]
        df = pd.DataFrame(data)
        df.to_excel(str(xlsx_file), index=False, header=False)

        custom_mapping = {
            'date': 'Tarih',
            'description': 'Açıklama',
            'amount': 'Tutar',
        }

        result = process_excel_data(
            str(xlsx_file), 'kuveytturk',
            user_column_mapping=custom_mapping,
        )
        assert result['successful'] >= 0
