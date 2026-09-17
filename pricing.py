"""
Fiyatlandirma is mantigi (business logic).

Bu modul, uygulamanin en kritik kuralini barindirir:
"Sistem ASLA taban fiyatin altinda bir fiyat onermez."

Tum hesaplamalar saf fonksiyonlardir (yan etkisiz) -> test edilmesi kolaydir.
"""
from dataclasses import dataclass
from typing import Optional


def calculate_base_price(cost: float, min_profit_rate: float) -> float:
    """
    Taban Fiyat = Maliyet * (1 + Minimum Kar Orani / 100)

    Ornek: Maliyet 100 TL, Kar %10  ->  Taban Fiyat = 110 TL
    """
    if cost < 0:
        raise ValueError("Maliyet negatif olamaz.")
    if min_profit_rate < 0:
        raise ValueError("Minimum kar orani negatif olamaz.")

    base_price = cost * (1 + min_profit_rate / 100)
    return round(base_price, 2)


@dataclass
class PriceRecommendation:
    base_price: float                 # Taban fiyat (asla altina inilmez)
    current_price: float              # Saticinin su anki fiyati
    market_price: Optional[float]      # Piyasada gorulen fiyat (tarama sonucu)
    recommended_price: Optional[float] # Onerilen yeni fiyat (None = oneri yok)
    action_needed: bool                # Panelde "aksiyon gerekli" olarak gosterilsin mi?
    reason: str                        # Kullaniciya gosterilecek kisa aciklama


# Piyasa fiyatinin ne kadar altinda bir fiyat onerecegimizi belirleyen guvenlik payi.
# Rakibin tam fiyatini degil, biraz altini onermek satisi rekabetci kilar.
UNDERCUT_MARGIN = 0.02  # %2

# Bildirim tetiklenmesi icin gereken minimum fark (TL bazinda kucuk gurultuyu elemek icin).
MIN_MEANINGFUL_GAP = 1.0


def evaluate_price(
    cost: float,
    min_profit_rate: float,
    current_price: float,
    market_price: Optional[float],
) -> PriceRecommendation:
    """
    Bir urunun mevcut durumunu degerlendirir ve GUVENLI bir oneri uretir.

    Kurallar (oncelik sirasiyla):
    1) Taban fiyat her zaman hesaplanir ve ASLA ihlal edilmez.
    2) Piyasa fiyati bilinmiyorsa oneri yapilmaz.
    3) Piyasa fiyati, satici fiyatindan yuksekse ve satici geride kaldiysa
       -> "fiyati yukselt" onerisi tetiklenir.
    4) Piyasa fiyati dusmus olsa bile ASLA "fiyati dusur" onerisi verilmez
       (Ters Enflasyon Korumasi). Sistem bu durumda sessiz kalir / bilgi verir
       ama taban fiyatin altina inmeyi hicbir zaman onermez.
    """
    base_price = calculate_base_price(cost, min_profit_rate)

    if market_price is None:
        return PriceRecommendation(
            base_price=base_price,
            current_price=current_price,
            market_price=None,
            recommended_price=None,
            action_needed=False,
            reason="Henuz piyasa taramasi yapilmadi.",
        )

    # --- TERS ENFLASYON KORUMASI ---
    # Piyasa fiyati taban fiyatin bile altindeyse, sistem hicbir sekilde
    # bir "dusur" onerisi uretmez. Sadece bilgilendirme amacli bir durum dondurulur.
    if market_price <= base_price:
        return PriceRecommendation(
            base_price=base_price,
            current_price=current_price,
            market_price=market_price,
            recommended_price=None,
            action_needed=False,
            reason=(
                "Piyasa fiyati taban fiyatinizin altinda/esit. Kar marjinizi korumak "
                "icin fiyat dusurme onerisi sunulmuyor."
            ),
        )

    # Piyasa satici fiyatindan yuksek degilse (yani satici zaten rekabetciyse) oneri yok.
    if market_price <= current_price + MIN_MEANINGFUL_GAP:
        return PriceRecommendation(
            base_price=base_price,
            current_price=current_price,
            market_price=market_price,
            recommended_price=None,
            action_needed=False,
            reason="Fiyatiniz piyasa ile uyumlu, aksiyon gerekmiyor.",
        )

    # Piyasa yukselmis ve satici geride kalmis -> oneri hesapla.
    raw_suggestion = market_price * (1 - UNDERCUT_MARGIN)

    # GUVENLIK KATMANI: hesaplanan oneri ne olursa olsun taban fiyatin altina inemez.
    recommended_price = max(base_price, round(raw_suggestion, 2))

    # Oneri, mevcut fiyattan anlamli derecede yuksek degilse tetikleme.
    if recommended_price <= current_price + MIN_MEANINGFUL_GAP:
        return PriceRecommendation(
            base_price=base_price,
            current_price=current_price,
            market_price=market_price,
            recommended_price=None,
            action_needed=False,
            reason="Piyasa hareketi mevcut fiyatinizi degistirecek kadar buyuk degil.",
        )

    return PriceRecommendation(
        base_price=base_price,
        current_price=current_price,
        market_price=market_price,
        recommended_price=recommended_price,
        action_needed=True,
        reason=(
            f"Piyasa fiyati {market_price:.2f} TL'ye yukseldi, mevcut fiyatiniz "
            f"{current_price:.2f} TL. Onerilen yeni fiyat: {recommended_price:.2f} TL."
        ),
    )
