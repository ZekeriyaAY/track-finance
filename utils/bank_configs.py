# -*- coding: utf-8 -*-
"""
Banka Excel formatları için konfigürasyon dosyası
Her bankanın Excel export formatını tanımlar
"""

BANK_CONFIGS = {
    'yapıkredi': {
        'name': 'Yapı Kredi',
        'columns': {
            'date': ['İşlem Tarihi', 'Tarih'],
            'description': ['İşlemler', 'İşlem Açıklaması', 'Açıklama'],
            'amount': ['Tutar', 'Miktar']
        },
        'date_format': '%d/%m/%Y',  # Excel'de 10/06/2025 formatında görünüyor
        'skip_rows': 0,
        'encoding': 'utf-8'
    }
}

def get_bank_config(bank_code):
    """Banka koduna göre konfigürasyonu döndürür"""
    return BANK_CONFIGS.get(bank_code)
