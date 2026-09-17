from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=1, max_length=64, description="Urun barkodu / SKU")
    product_name: str = Field(..., min_length=1, max_length=255)
    cost: float = Field(..., gt=0, description="Maliyet (TL)")
    min_profit_rate: float = Field(..., ge=0, description="Minimum kar orani (%)")
    current_price: float = Field(..., gt=0, description="Mevcut satis fiyati (TL)")
    competitor_url: Optional[str] = Field(None, max_length=500)

    @field_validator("current_price")
    @classmethod
    def warn_if_below_cost(cls, v, info):
        cost = info.data.get("cost")
        if cost is not None and v < cost:
            raise ValueError("Mevcut satis fiyati maliyetin altinda olamaz.")
        return v


class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    cost: Optional[float] = Field(None, gt=0)
    min_profit_rate: Optional[float] = Field(None, ge=0)
    current_price: Optional[float] = Field(None, gt=0)
    competitor_url: Optional[str] = Field(None, max_length=500)


class ApplyRecommendation(BaseModel):
    # Kullanici onerilen fiyati degistirmeden onaylayabilir ya da elle bir
    # fiyat girebilir (ornegin 124.90 gibi psikolojik fiyatlandirma icin).
    new_price: Optional[float] = Field(None, gt=0)


class ProductOut(BaseModel):
    id: int
    sku: str
    product_name: str
    cost: float
    min_profit_rate: float
    current_price: float
    market_price: Optional[float]
    market_price_source: Optional[str]
    competitor_url: Optional[str]
    last_scanned_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    # Turetilmis (hesaplanan) alanlar - DB'de tutulmaz, her istekte hesaplanir.
    base_price: float
    recommended_price: Optional[float]
    action_needed: bool
    reason: str

    class Config:
        from_attributes = True


class ScanResult(BaseModel):
    scanned_count: int
    action_needed_count: int
