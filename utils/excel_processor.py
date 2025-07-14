# -*- coding: utf-8 -*-
"""
Excel ve CSV dosyalarını işlemek için yardımcı fonksiyonlar
"""

import pandas as pd
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
from utils.bank_configs import get_bank_config

logger = logging.getLogger(__name__)

class ExcelImportError(Exception):
    """Excel import işlemi sırasında oluşan hatalar"""
    pass

def parse_turkish_amount(amount_str):
    """
    Türkçe format tutarları parse eder
    Örnek: "1.234,56" -> 1234.56
    Yapı Kredi için: "+386,50 TL" -> (386.50, "income")
                     "386,50 TL" -> (386.50, "expense")
    """
    if pd.isna(amount_str) or amount_str == '':
        return 0.0, 'expense'
    
    # String'e çevir
    amount_str = str(amount_str).strip()
    
    # Boş string kontrolü
    if not amount_str:
        return 0.0, 'expense'
    
    # + işareti income, - işareti veya hiçbir işaret expense
    is_income = amount_str.startswith('+')
    is_expense = amount_str.startswith('-')
    
    # + veya - işaretini kaldır
    if is_income or is_expense:
        amount_str = amount_str[1:]
    
    # Parantez içindeki tutarlar negatif (bazı bankalar böyle gösterir)
    is_negative = amount_str.startswith('(') and amount_str.endswith(')')
    if is_negative:
        amount_str = amount_str[1:-1]
        is_expense = True
        is_income = False
    
    # Sadece sayı karakterleri, nokta, virgül bırak (TL, ₺ gibi para birimi sembollerini temizle)
    amount_str = re.sub(r'[^\d.,-]', '', amount_str)
    
    # Türkçe format: binlik ayırıcısı nokta, ondalık ayırıcısı virgül
    if ',' in amount_str:
        # Virgülden önceki kısmda noktalar binlik ayırıcısı
        parts = amount_str.split(',')
        if len(parts) == 2:
            integer_part = parts[0].replace('.', '')
            decimal_part = parts[1]
            amount_str = f"{integer_part}.{decimal_part}"
        else:
            # Virgül sayısı > 1, hatalı format
            amount_str = amount_str.replace(',', '').replace('.', '')
    else:
        # Virgül yok, noktalar binlik ayırıcısı olabilir
        if amount_str.count('.') > 1:
            # Birden fazla nokta varsa, sonuncusu ondalık ayırıcısı
            last_dot_index = amount_str.rfind('.')
            integer_part = amount_str[:last_dot_index].replace('.', '')
            decimal_part = amount_str[last_dot_index+1:]
            amount_str = f"{integer_part}.{decimal_part}"
        elif amount_str.count('.') == 1:
            # Tek nokta var, bu ondalık ayırıcısı mı binlik ayırıcısı mı?
            dot_index = amount_str.find('.')
            after_dot = amount_str[dot_index+1:]
            if len(after_dot) <= 2:
                # 2 hane veya daha az, ondalık ayırıcısı olabilir
                pass
            else:
                # 2 haneden fazla, binlik ayırıcısı
                amount_str = amount_str.replace('.', '')
    
    try:
        result = float(amount_str)
        # Type'ı belirle
        if is_income:
            transaction_type = 'income'
        else:
            transaction_type = 'expense'
        
        return abs(result), transaction_type  # Amount her zaman pozitif
    except ValueError:
        logger.warning(f"Could not parse amount: {amount_str}")
        return 0.0, 'expense'

def parse_date(date_str, date_format='%d.%m.%Y'):
    """
    Tarih string'ini parse eder
    """
    if pd.isna(date_str):
        return None
    
    date_str = str(date_str).strip()
    
    # Excel'den gelen sayısal tarih formatını kontrol et
    try:
        # Excel serial date number
        if date_str.isdigit() and len(date_str) > 4:
            excel_date = int(date_str)
            # Excel'de 1900-01-01 = 1 (ama aslında 1899-12-30)
            excel_epoch = datetime(1899, 12, 30)
            return excel_epoch + pd.Timedelta(days=excel_date)
    except:
        pass
    
    # String tarih formatlarını dene
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

def read_excel_file(file_path, bank_config=None):
    """
    Excel dosyasını okur ve DataFrame olarak döndürür
    """
    try:
        # Excel dosyaları için encoding gerekmiyor, direkt okuyabiliriz
        df = pd.read_excel(file_path)
        return df
    
    except Exception as e:
        raise ExcelImportError(f"Excel dosyası okunamadı: {str(e)}")

def read_csv_file(file_path):
    """
    CSV dosyasını okur ve DataFrame olarak döndürür
    """
    try:
        # CSV dosyaları için farklı encoding'leri dene
        encodings = ['utf-8', 'latin-1', 'cp1254', 'iso-8859-9']
        
        df = None
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            df = pd.read_csv(file_path)
        
        return df
    
    except Exception as e:
        raise ExcelImportError(f"CSV dosyası okunamadı: {str(e)}")

def map_columns(df, bank_config):
    """
    DataFrame kolonlarını banka konfigürasyonuna göre eşleştirir
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
    Excel/CSV dosyasını işler ve transaction listesi döndürür
    """
    bank_config = get_bank_config(bank_code)
    if not bank_config:
        raise ExcelImportError(f"Bilinmeyen banka kodu: {bank_code}")
    
    try:
        # Dosya uzantısına göre doğru okuma fonksiyonunu seç
        file_extension = file_path.lower().split('.')[-1]
        if file_extension == 'csv':
            df = read_csv_file(file_path)
        elif file_extension in ['xlsx', 'xls']:
            df = read_excel_file(file_path, bank_config)
        else:
            raise ExcelImportError(f"Desteklenmeyen dosya formatı: {file_extension}")
        
        # Skip rows if configured
        if bank_config.get('skip_rows', 0) > 0:
            logger.info(f"Skipping {bank_config['skip_rows']} rows. Original shape: {df.shape}")
            df = df.iloc[bank_config['skip_rows']:].reset_index(drop=True)
            logger.info(f"After skipping rows: {df.shape}")
        
        logger.info(f"DataFrame columns: {list(df.columns)}")
        logger.info(f"DataFrame shape: {df.shape}")
        logger.info(f"First few rows:\n{df.head()}")
        
        # Kolon eşleştirmesi
        if user_column_mapping:
            column_mapping = user_column_mapping
        else:
            column_mapping = map_columns(df, bank_config)
        
        # Gerekli kolonların varlığını kontrol et
        required_fields = ['date', 'description', 'amount']
        missing_fields = [field for field in required_fields if field not in column_mapping]
        
        if missing_fields:
            raise ExcelImportError(f"Gerekli kolonlar bulunamadı: {', '.join(missing_fields)}")
        
        transactions = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Tarih
                date_col = column_mapping['date']
                date_value = parse_date(row[date_col], bank_config['date_format'])
                
                # Açıklama
                desc_col = column_mapping['description']
                description = str(row[desc_col]).strip()
                
                # Tutar ve type'ı parse et
                amount_col = column_mapping['amount']
                amount, transaction_type = parse_turkish_amount(row[amount_col])
                
                # Amount 0 olan satırları da atla
                if amount == 0:
                    logger.debug(f"Skipping zero amount row {index + 1}: amount={amount}")
                    continue
                
                logger.debug(f"Processing row {index + 1}: date={date_value}, desc='{description[:50]}...', amount={amount}, type={transaction_type}")
                
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
        raise ExcelImportError(f"Excel işleme hatası: {str(e)}")
