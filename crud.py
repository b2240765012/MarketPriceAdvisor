from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException

from . import models, schemas, pricing
from .scraper import get_active_provider


def _to_out(product: models.Product) -> schemas.ProductOut:
    """ORM nesnesini, hesaplanan (taban fiyat / oneri) alanlarla zenginlestirip API ciktisina cevirir."""
    evaluation = pricing.evaluate_price(
        cost=product.cost,
        min_profit_rate=product.min_profit_rate,
        current_price=product.current_price,
        market_price=product.market_price,
    )
    return schemas.ProductOut(
        id=product.id,
        sku=product.sku,
        product_name=product.product_name,
        cost=product.cost,
        min_profit_rate=product.min_profit_rate,
        current_price=product.current_price,
        market_price=product.market_price,
        market_price_source=product.market_price_source,
        competitor_url=product.competitor_url,
        last_scanned_at=product.last_scanned_at,
        created_at=product.created_at,
        updated_at=product.updated_at,
        base_price=evaluation.base_price,
        recommended_price=evaluation.recommended_price,
        action_needed=evaluation.action_needed and not product.recommendation_dismissed,
        reason=evaluation.reason,
    )


def create_product(db: Session, data: schemas.ProductCreate) -> schemas.ProductOut:
    existing = db.query(models.Product).filter(models.Product.sku == data.sku).first()
    if existing:
        raise HTTPException(status_code=409, detail="Bu SKU/barkod ile bir urun zaten kayitli.")

    product = models.Product(
        sku=data.sku,
        product_name=data.product_name,
        cost=data.cost,
        min_profit_rate=data.min_profit_rate,
        current_price=data.current_price,
        competitor_url=data.competitor_url,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return _to_out(product)


def list_products(db: Session) -> List[schemas.ProductOut]:
    products = db.query(models.Product).order_by(models.Product.created_at.desc()).all()
    return [_to_out(p) for p in products]


def get_product_or_404(db: Session, product_id: int) -> models.Product:
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Urun bulunamadi.")
    return product


def get_product(db: Session, product_id: int) -> schemas.ProductOut:
    return _to_out(get_product_or_404(db, product_id))


def update_product(db: Session, product_id: int, data: schemas.ProductUpdate) -> schemas.ProductOut:
    product = get_product_or_404(db, product_id)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return _to_out(product)


def delete_product(db: Session, product_id: int) -> None:
    product = get_product_or_404(db, product_id)
    db.delete(product)
    db.commit()


def scan_product(db: Session, product_id: int) -> schemas.ProductOut:
    """Tek bir urun icin piyasa fiyatini tarar (mock ya da gercek scraper uzerinden)."""
    product = get_product_or_404(db, product_id)
    provider = get_active_provider()

    result = provider.fetch_price(
        sku=product.sku,
        competitor_url=product.competitor_url,
        reference_price=product.current_price,
    )

    if result.price is not None:
        product.market_price = result.price
        product.market_price_source = result.source
        product.last_scanned_at = datetime.utcnow()
        # Piyasa yeniden hareketlendigi icin onceki "reddedilmis" durumunu sifirla,
        # boylece kullanici guncel bir fiyat degisimini kacirmasin.
        product.recommendation_dismissed = False
        db.commit()
        db.refresh(product)

    return _to_out(product)


def scan_all_products(db: Session) -> schemas.ScanResult:
    """Tum urunler icin piyasa taramasi yapar. Scheduler ve manuel 'Tumunu Tara' butonu tarafindan kullanilir."""
    products = db.query(models.Product).all()
    action_needed_count = 0

    for product in products:
        result = scan_product(db, product.id)
        if result.action_needed:
            action_needed_count += 1

    return schemas.ScanResult(scanned_count=len(products), action_needed_count=action_needed_count)


def list_recommendations(db: Session) -> List[schemas.ProductOut]:
    """Sadece aksiyon alinmasi gereken (piyasasi yukselmis) urunleri dondurur."""
    all_products = list_products(db)
    return [p for p in all_products if p.action_needed]


def apply_recommendation(db: Session, product_id: int, payload: schemas.ApplyRecommendation) -> schemas.ProductOut:
    """
    Kullanici onerilen (ya da elle girdigi) fiyati ONAYLADIGINDA cagrilir.

    ONEMLI: Bu fonksiyon sadece kullanici acikca bir butona bastiginda calisir.
    Sistem hicbir zaman kendiliginden current_price alanini degistirmez.
    """
    product = get_product_or_404(db, product_id)
    evaluation = pricing.evaluate_price(
        cost=product.cost,
        min_profit_rate=product.min_profit_rate,
        current_price=product.current_price,
        market_price=product.market_price,
    )

    new_price = payload.new_price if payload.new_price is not None else evaluation.recommended_price

    if new_price is None:
        raise HTTPException(status_code=400, detail="Uygulanacak bir fiyat onerisi bulunmuyor.")

    # SON GUVENLIK KONTROLU: kullanici elle bir fiyat girse dahi taban fiyatin
    # altina inilmesine izin verilmez.
    if new_price < evaluation.base_price:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Girilen fiyat ({new_price:.2f} TL) taban fiyatin ({evaluation.base_price:.2f} TL) "
                "altinda olamaz. Kar marjinizi korumak icin bu islem engellendi."
            ),
        )

    product.current_price = round(new_price, 2)
    product.recommendation_dismissed = True  # onerildi ve uygulandi, tekrar gosterme
    db.commit()
    db.refresh(product)
    return _to_out(product)


def dismiss_recommendation(db: Session, product_id: int) -> schemas.ProductOut:
    """Kullanici oneriyi gormezden gelmek isterse (fiyati degistirmeden kapatir)."""
    product = get_product_or_404(db, product_id)
    product.recommendation_dismissed = True
    db.commit()
    db.refresh(product)
    return _to_out(product)
