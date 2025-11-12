# -*- coding: utf-8 -*-
"""
Helper functions for processing Excel and CSV files
"""

import pandas as pd
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
from utils.bank_configs import get_bank_config

logger = logging.getLogger(__name__)

class ExcelImportError(Exception):
    """Errors that occur during Excel import process"""
    pass

def parse_turkish_amount(amount_str):
    """
    Parse Turkish format amounts
    Example: "1.234,56" -> 1234.56
    For Yapı Kredi: "+386,50 TL" -> (386.50, "income")
                    "386,50 TL" -> (386.50, "expense")
    """
    if pd.isna(amount_str) or amount_str == '':
        return 0.0, 'expense'
    
    # Convert to string
    amount_str = str(amount_str).strip()
    
    # Empty string check
    if not amount_str:
        return 0.0, 'expense'
    
    # + sign means income, - sign or no sign means expense
    is_income = amount_str.startswith('+')
    is_expense = amount_str.startswith('-')
    
    # Remove + or - sign
    if is_income or is_expense:
        amount_str = amount_str[1:]
    
    # Amounts in parentheses are negative (some banks show this way)
    is_negative = amount_str.startswith('(') and amount_str.endswith(')')
    if is_negative:
        amount_str = amount_str[1:-1]
        is_expense = True
        is_income = False
    
    # Keep only numeric characters, dots, commas (remove currency symbols like TL, ₺)
    amount_str = re.sub(r'[^\d.,-]', '', amount_str)
    
    # Turkish format: thousand separator is dot, decimal separator is comma
    if ',' in amount_str:
        # Dots before comma are thousand separators
        parts = amount_str.split(',')
        if len(parts) == 2:
            integer_part = parts[0].replace('.', '')
            decimal_part = parts[1]
            amount_str = f"{integer_part}.{decimal_part}"
        else:
            # More than 1 comma, invalid format
            amount_str = amount_str.replace(',', '').replace('.', '')
    else:
        # No comma, dots might be thousand separators
        if amount_str.count('.') > 1:
            # Multiple dots, last one is decimal separator
            last_dot_index = amount_str.rfind('.')
            integer_part = amount_str[:last_dot_index].replace('.', '')
            decimal_part = amount_str[last_dot_index+1:]
            amount_str = f"{integer_part}.{decimal_part}"
        elif amount_str.count('.') == 1:
            # Single dot, is it decimal or thousand separator?
            dot_index = amount_str.find('.')
            after_dot = amount_str[dot_index+1:]
            if len(after_dot) <= 2:
                # 2 digits or less, could be decimal separator
                pass
            else:
                # More than 2 digits, thousand separator
                amount_str = amount_str.replace('.', '')
    
    try:
        result = float(amount_str)
        # Determine type
        if is_income:
            transaction_type = 'income'
        else:
            transaction_type = 'expense'
        
        return abs(result), transaction_type  # Amount is always positive
    except ValueError:
        logger.warning(f"Could not parse amount: {amount_str}")
        return 0.0, 'expense'

def parse_date(date_str, date_format='%d.%m.%Y'):
    """
    Parse date string
    """
    if pd.isna(date_str):
        return None
    
    date_str = str(date_str).strip()
    
    # Check Excel numeric date format
    try:
        # Excel serial date number
        if date_str.isdigit() and len(date_str) > 4:
            excel_date = int(date_str)
            # Excel 1900-01-01 = 1 (but actually 1899-12-30)
            excel_epoch = datetime(1899, 12, 30)
            return excel_epoch + pd.Timedelta(days=excel_date)
    except:
        pass
    
    # Try string date formats
    date_formats = [
        date_format,
        '%d.%m.%Y',
        '%d/%m/%Y',
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%d.%m.%y',
        '%d/%m/%y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Could not parse date: {date_str}")

def read_file_with_header_detection(file_path, bank_config=None):
    """
    Read Excel or CSV file and return as DataFrame
    Dynamically finds the header row if bank_config has header_row_identifier
    """
    try:
        file_extension = file_path.lower().split('.')[-1]
        
        # Read file without header first
        if file_extension == 'csv':
            # Try different encodings for CSV files
            encodings = ['utf-8', 'latin-1', 'cp1254', 'iso-8859-9']
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, header=None)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                df = pd.read_csv(file_path, header=None)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(file_path, header=None)
        else:
            raise ExcelImportError(f"Unsupported file format: {file_extension}")
        
        # If bank config has header identifier, find the header row
        if bank_config and bank_config.get('header_row_identifier'):
            header_identifier = bank_config['header_row_identifier']
            header_row = None
            
            for idx, row in df.iterrows():
                if header_identifier in str(row.values):
                    header_row = idx
                    break
            
            if header_row is not None:
                # Set the header row and return data after header
                df.columns = df.iloc[header_row]
                df = df.iloc[header_row + 1:].reset_index(drop=True)
                logger.info(f"Found header row at index {header_row}")
            else:
                # Fallback: try to read normally with first row as header
                if file_extension == 'csv':
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)
                logger.warning(f"Header row identifier '{header_identifier}' not found, using first row as header")
        else:
            # No header identifier, read normally with first row as header
            if file_extension == 'csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        
        return df
    
    except Exception as e:
        raise ExcelImportError(f"Could not read file: {str(e)}")

def map_columns(df, bank_config):
    """
    Map DataFrame columns according to bank configuration
    """
    column_mapping = {}
    
    for field_type, possible_names in bank_config['columns'].items():
        for possible_name in possible_names:
            for col in df.columns:
                if str(col).strip().lower() == possible_name.lower():
                    column_mapping[field_type] = col
                    break
            if field_type in column_mapping:
                break
    
    return column_mapping

def process_excel_data(file_path, bank_code, user_column_mapping=None):
    """
    Process Excel/CSV file and return transaction list
    """
    bank_config = get_bank_config(bank_code)
    if not bank_config:
        raise ExcelImportError(f"Unknown bank code: {bank_code}")
    
    try:
        # Read file with automatic header detection
        df = read_file_with_header_detection(file_path, bank_config)
        
        # Skip initial data rows if configured (e.g., previous period debt rows)
        skip_initial_rows = bank_config.get('skip_initial_rows', 0)
        if skip_initial_rows > 0:
            df = df.iloc[skip_initial_rows:].reset_index(drop=True)
            logger.info(f"Skipped first {skip_initial_rows} data rows")
        
        # Column mapping
        if user_column_mapping:
            column_mapping = user_column_mapping
        else:
            column_mapping = map_columns(df, bank_config)
        
        # Check for required columns
        required_fields = ['date', 'description', 'amount']
        missing_fields = [field for field in required_fields if field not in column_mapping]
        
        if missing_fields:
            raise ExcelImportError(f"Required columns not found: {', '.join(missing_fields)}")
        
        transactions = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Date
                date_col = column_mapping['date']
                date_value = parse_date(row[date_col], bank_config['date_format'])
                
                # Description
                desc_col = column_mapping['description']
                description = str(row[desc_col]).strip()
                
                # Parse amount and type
                amount_col = column_mapping['amount']
                amount, transaction_type = parse_turkish_amount(row[amount_col])
                
                # Skip rows with zero amount
                if amount == 0:
                    continue
                
                transactions.append({
                    'date': date_value,
                    'description': description,
                    'amount': amount,
                    'type': transaction_type,
                    'source_row': index + 1
                })
                
            except Exception as e:
                errors.append({
                    'row': index + 1,
                    'error': str(e),
                    'data': dict(row)
                })
                continue
        
        return {
            'transactions': transactions,
            'errors': errors,
            'total_processed': len(df),
            'successful': len(transactions),
            'failed': len(errors)
        }
    
    except Exception as e:
        raise ExcelImportError(f"Excel processing error: {str(e)}")
