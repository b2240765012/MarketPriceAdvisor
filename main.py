import logging

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import engine, get_db
from .scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dinamik Piyasa Takip ve Fiyat Oneri Sistemi",
    description=(
        "Satici karini koruyan, piyasa fiyat degisimlerine gore ONERI ve BILDIRIM "
        "sunan (fiyatlari ASLA otomatik degistirmeyen) yari-otonom fiyatlandirma sistemi."
    ),
    version="1.0.0",
)

# Gelistirme asamasinda frontend'in (Vite, varsayilan port 5173) API'ye erisebilmesi icin.
# Prod ortaminda allow_origins'i kendi domain'inizle sinirlandirin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    start_scheduler(hour=3, minute=0)  # her gun 03:00'te otomatik tarama


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "market-price-advisor"}


# --------------------------------------------------------------------------
# Urun (Product) CRUD
# --------------------------------------------------------------------------

@app.post("/products", response_model=schemas.ProductOut, tags=["Urunler"], status_code=201)
def create_product(data: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Yeni bir urun ekler (Urun Adi, Maliyet, Min Kar %, Mevcut Fiyat, Rakip URL/SKU)."""
    return crud.create_product(db, data)


@app.get("/products", response_model=list[schemas.ProductOut], tags=["Urunler"])
def list_products(db: Session = Depends(get_db)):
    """Tum urunleri, taban fiyat/piyasa fiyati/oneri bilgileriyle birlikte listeler."""
    return crud.list_products(db)


@app.get("/products/{product_id}", response_model=schemas.ProductOut, tags=["Urunler"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    return crud.get_product(db, product_id)


@app.put("/products/{product_id}", response_model=schemas.ProductOut, tags=["Urunler"])
def update_product(product_id: int, data: schemas.ProductUpdate, db: Session = Depends(get_db)):
    return crud.update_product(db, product_id, data)


@app.delete("/products/{product_id}", tags=["Urunler"], status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    crud.delete_product(db, product_id)
    return None


# --------------------------------------------------------------------------
# Piyasa Tarama (Scan)
# --------------------------------------------------------------------------

@app.post("/products/{product_id}/scan", response_model=schemas.ProductOut, tags=["Piyasa Tarama"])
def scan_single_product(product_id: int, db: Session = Depends(get_db)):
    """Tek bir urun icin anlik piyasa taramasi tetikler (test/manuel kullanim icin)."""
    return crud.scan_product(db, product_id)


@app.post("/scan-all", response_model=schemas.ScanResult, tags=["Piyasa Tarama"])
def scan_all(db: Session = Depends(get_db)):
    """Tum urunler icin piyasa taramasini manuel olarak tetikler."""
    return crud.scan_all_products(db)


# --------------------------------------------------------------------------
# Oneriler ve Bildirimler
# --------------------------------------------------------------------------

@app.get("/recommendations", response_model=list[schemas.ProductOut], tags=["Oneriler"])
def get_recommendations(db: Session = Depends(get_db)):
    """Sadece piyasasi yukselmis ve aksiyon gerektiren urunleri dondurur."""
    return crud.list_recommendations(db)


@app.post("/products/{product_id}/apply-recommendation", response_model=schemas.ProductOut, tags=["Oneriler"])
def apply_recommendation(product_id: int, payload: schemas.ApplyRecommendation, db: Session = Depends(get_db)):
    """
    Kullanici 'Onerilen Fiyati Uygula' butonuna bastiginda cagrilir.
    Bu, satici fiyatinin (current_price) degistigi TEK yerdir; sistem
    bunu kendiliginden asla yapmaz.
    """
    return crud.apply_recommendation(db, product_id, payload)


@app.post("/products/{product_id}/dismiss-recommendation", response_model=schemas.ProductOut, tags=["Oneriler"])
def dismiss_recommendation(product_id: int, db: Session = Depends(get_db)):
    """Kullanici oneriyi fiyat degistirmeden kapatmak isterse."""
    return crud.dismiss_recommendation(db, product_id)
