from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func

from .database import Base


class Product(Base):
    """
    Products tablosu.

    Not: base_price (taban fiyat) ve recommended_price (onerilen fiyat) bilerek
    veritabaninda SAKLANMAZ; her zaman cost ve min_profit_rate'ten anlik olarak
    hesaplanir (bkz. app/pricing.py). Boylece kar orani degisince taban fiyat
    otomatik ve tutarli sekilde guncellenir, "bayat" veri riski olusmaz.
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(64), unique=True, index=True, nullable=False)
    product_name = Column(String(255), nullable=False)

    cost = Column(Float, nullable=False)                 # Maliyet
    min_profit_rate = Column(Float, nullable=False)       # Minimum Kar Orani (%)
    current_price = Column(Float, nullable=False)         # Mevcut Satis Fiyati

    market_price = Column(Float, nullable=True)           # Son taranan piyasa fiyati
    market_price_source = Column(String(255), nullable=True)   # Hangi kaynaktan geldigi (mock/gercek scraper adi)
    competitor_url = Column(String(500), nullable=True)    # Rakip / piyasa URL'si (gercek scraper icin)

    last_scanned_at = Column(DateTime, nullable=True)

    # Kullanici bir oneriyi uyguladiginda veya reddettiginde tekrar tekrar
    # ayni bildirimi gormesin diye basit bir durum bayragi tutuyoruz.
    recommendation_dismissed = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
