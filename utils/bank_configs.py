# -*- coding: utf-8 -*-
"""
Bank Excel format configuration file
Defines Excel export format for each bank
"""

BANK_CONFIGS = {
    'yapikredi': {
        'name': 'Yapı Kredi',
        'columns': {
            'date': ['İşlem Tarihi', 'Tarih'],
            'description': ['İşlemler', 'İşlem Açıklaması', 'Açıklama'],
            'amount': ['Tutar', 'Miktar']
        },
        'date_format': '%d/%m/%Y',
        'header_row_identifier': 'İşlem Tarihi',  # Used to find header row
        'encoding': 'utf-8',
        'skip_initial_rows': 2  # Skip first 2 data rows after header (previous period debt)
    },
    'kuveytturk': {
        'name': 'Kuveyt Türk',
        'columns': {
            'date': ['Tarih'],
            'description': ['Açıklama'],
            'amount': ['Tutar']
        },
        'date_format': None,  # Not used - Excel returns datetime objects directly
        'header_row_identifier': 'Tarih',  # Used to find header row
        'encoding': 'utf-8',
        'skip_initial_rows': 0,
        'use_bold_for_income': True  # Bold rows are income/refund transactions (card info rows are automatically skipped as they have no date)
    }
}

def get_bank_config(bank_code):
    """Returns configuration for given bank code"""
    return BANK_CONFIGS.get(bank_code)
 