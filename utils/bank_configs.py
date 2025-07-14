# -*- coding: utf-8 -*-
"""
Bank Excel format configuration file
Defines Excel export format for each bank
"""

BANK_CONFIGS = {
    'yapıkredi': {
        'name': 'Yapı Kredi',
        'columns': {
            'date': ['İşlem Tarihi', 'Tarih'],
            'description': ['İşlemler', 'İşlem Açıklaması', 'Açıklama'],
            'amount': ['Tutar', 'Miktar']
        },
        'date_format': '%d/%m/%Y',  # Excel format appears as 10/06/2025
        'skip_rows': 0,
        'encoding': 'utf-8'
    }
}

def get_bank_config(bank_code):
    """Returns configuration for given bank code"""
    return BANK_CONFIGS.get(bank_code)
 