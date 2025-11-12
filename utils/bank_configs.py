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
    }
}

def get_bank_config(bank_code):
    """Returns configuration for given bank code"""
    return BANK_CONFIGS.get(bank_code)
 