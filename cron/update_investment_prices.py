from services.investment_service import InvestmentService

def update_prices():
    """Yatırım fiyatlarını günceller."""
    try:
        InvestmentService.update_investment_prices()
        print("Yatırım fiyatları başarıyla güncellendi.")
    except Exception as e:
        print(f"Yatırım fiyatları güncellenirken hata oluştu: {str(e)}")

if __name__ == "__main__":
    update_prices() 