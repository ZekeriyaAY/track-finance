import requests
from datetime import datetime, date
import logging
from models.investment import Investment
from models.investment_history import InvestmentHistory
from models.__init__ import db

# Loglama ayarları
logger = logging.getLogger(__name__)

class InvestmentService:
    """Yatırım işlemleri için servis sınıfı."""
    
    @staticmethod
    def update_investment_prices():
        """Tüm yatırımların güncel fiyatlarını günceller."""
        investments = Investment.query.all()
        
        for investment in investments:
            # Yatırım türüne göre fiyat güncelleme
            if investment.type.code == 'gold':
                price = InvestmentService._get_gold_price()
            elif investment.type.code == 'btc':
                price = InvestmentService._get_btc_price()
            elif investment.type.code == 'eth':
                price = InvestmentService._get_eth_price()
            elif investment.type.code == 'usd':
                price = InvestmentService._get_usd_price()
            elif investment.type.code == 'eur':
                price = InvestmentService._get_eur_price()
            else:
                continue  # Diğer yatırım türleri için fiyat güncelleme yok
            
            if price:
                # Güncel fiyatı güncelle
                investment.current_price = price
                
                # Geçmiş kaydı oluştur
                history = InvestmentHistory(
                    investment_id=investment.id,
                    price=price,
                    date=date.today()
                )
                
                db.session.add(history)
            else:
                logger.error(f"{investment.type.name} için fiyat güncellenemedi.")
        
        try:
            db.session.commit()
            logger.info("Yatırım fiyatları başarıyla güncellendi.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Yatırım fiyatları güncellenirken bir hata oluştu: {str(e)}")
    
    @staticmethod
    def _get_gold_price():
        """Altın fiyatını API'den çeker."""
        try:
            # Örnek API çağrısı (gerçek API'ye göre değiştirilmeli)
            response = requests.get('https://api.example.com/gold-price')
            data = response.json()
            return float(data['price'])
        except Exception as e:
            logger.error(f"Altın fiyatı alınamadı: {str(e)}")
            return None
    
    @staticmethod
    def _get_btc_price():
        """Bitcoin fiyatını API'den çeker."""
        try:
            # Örnek API çağrısı (gerçek API'ye göre değiştirilmeli)
            response = requests.get('https://api.example.com/btc-price')
            data = response.json()
            return float(data['price'])
        except Exception as e:
            logger.error(f"Bitcoin fiyatı alınamadı: {str(e)}")
            return None
    
    @staticmethod
    def _get_eth_price():
        """Ethereum fiyatını API'den çeker."""
        try:
            # Örnek API çağrısı (gerçek API'ye göre değiştirilmeli)
            response = requests.get('https://api.example.com/eth-price')
            data = response.json()
            return float(data['price'])
        except Exception as e:
            logger.error(f"Ethereum fiyatı alınamadı: {str(e)}")
            return None
    
    @staticmethod
    def _get_usd_price():
        """USD/TRY kurunu API'den çeker."""
        try:
            # Örnek API çağrısı (gerçek API'ye göre değiştirilmeli)
            response = requests.get('https://api.example.com/usd-price')
            data = response.json()
            return float(data['price'])
        except Exception as e:
            logger.error(f"USD fiyatı alınamadı: {str(e)}")
            return None
    
    @staticmethod
    def _get_eur_price():
        """EUR/TRY kurunu API'den çeker."""
        try:
            # Örnek API çağrısı (gerçek API'ye göre değiştirilmeli)
            response = requests.get('https://api.example.com/eur-price')
            data = response.json()
            return float(data['price'])
        except Exception as e:
            logger.error(f"EUR fiyatı alınamadı: {str(e)}")
            return None 