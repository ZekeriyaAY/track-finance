import logging
from services.investment_service import InvestmentService

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/investment_updates.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def update_prices():
    """Yatırım fiyatlarını günceller."""
    try:
        InvestmentService.update_investment_prices()
        logger.info("Yatırım fiyatları başarıyla güncellendi.")
    except Exception as e:
        logger.error(f"Yatırım fiyatları güncellenirken hata oluştu: {str(e)}")

if __name__ == "__main__":
    update_prices() 