"""
Piyasa Fiyati Tarama Servisi.

Bu modul BILEREK bir "interface" (soyut sinif) + "mock implementasyon"
seklinde tasarlandi. Ileride gercek bir web scraper veya bir pazar yeri
API'si (Trendyol, Hepsiburada vb.) eklemek istediginizde, tek yapmaniz
gereken MarketPriceProvider'i implemente eden yeni bir sinif yazip
get_active_provider() fonksiyonunda degistirmektir. Geri kalan tum
uygulama (endpoint'ler, scheduler, is mantigi) HICBIR SEKILDE degismez.

Ornek gercek implementasyon iskeleti asagida yorum satirinda gosterilmistir.
"""
import os
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class MarketPriceResult:
    price: Optional[float]
    source: str  # hangi saglayicidan/siteden geldigi bilgisi (loglama/gosterim icin)


class MarketPriceProvider(ABC):
    """Tum piyasa fiyati saglayicilarinin uymasi gereken ortak arayuz."""

    @abstractmethod
    def fetch_price(self, sku: str, competitor_url: Optional[str], reference_price: float) -> MarketPriceResult:
        """Bir urun icin piyasa fiyatini dondurur."""
        raise NotImplementedError


class MockMarketPriceProvider(MarketPriceProvider):
    """
    GELISTIRME/TEST amacli sahte (simulated) saglayici.

    Gercek bir siteyi taramak yerine, satici fiyatinin etrafinda rastgele
    ama makul bir piyasa fiyati uretir. Boylece scraping/anti-bot
    engelleriyle ugrasmadan tum sistemi (bildirimler, oneriler, UI) uctan
    uca test edebilirsiniz.
    """

    def __init__(self, min_variance: float = -0.15, max_variance: float = 0.25):
        # -%15 ile +%25 arasinda rastgele bir sapma uretir (piyasanin
        # cogunlukla yukselme egiliminde oldugu bir senaryoyu simule eder).
        self.min_variance = min_variance
        self.max_variance = max_variance

    def fetch_price(self, sku: str, competitor_url: Optional[str], reference_price: float) -> MarketPriceResult:
        variance = random.uniform(self.min_variance, self.max_variance)
        simulated_price = round(reference_price * (1 + variance), 2)
        simulated_price = max(simulated_price, 0.01)
        return MarketPriceResult(price=simulated_price, source="mock-simulator")


# ---------------------------------------------------------------------------
# GERCEK SCRAPER ICIN ISKELET (ileride kullanmak icin - su an devre disi)
# ---------------------------------------------------------------------------
# class TrendyolScraperProvider(MarketPriceProvider):
#     def fetch_price(self, sku, competitor_url, reference_price):
#         # 1) requests/httpx + BeautifulSoup veya Playwright ile competitor_url'i cek
#         # 2) Fiyat bilgisini DOM'dan parse et
#         # 3) MarketPriceResult(price=..., source="trendyol") dondur
#         # 4) Hata/engelleme durumunda MarketPriceResult(price=None, source="trendyol")
#         ...
# ---------------------------------------------------------------------------


def get_active_provider() -> MarketPriceProvider:
    """
    Aktif saglayiciyi dondurur. Ortam degiskeni ile kolayca degistirilebilir:

        MARKET_PROVIDER=mock   (varsayilan)
        MARKET_PROVIDER=trendyol  (ileride gercek scraper eklendiginde)
    """
    provider_name = os.getenv("MARKET_PROVIDER", "mock")

    if provider_name == "mock":
        return MockMarketPriceProvider()

    # Gelecekte gercek saglayicilar buraya eklenecek:
    # if provider_name == "trendyol":
    #     return TrendyolScraperProvider()

    raise ValueError(f"Bilinmeyen MARKET_PROVIDER: {provider_name}")
