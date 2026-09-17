# Fiyat Nöbeti — Dinamik Piyasa Takip ve Fiyat Öneri Sistemi

E-ticaret satıcılarının kâr marjını korumasına yardımcı olan, piyasa fiyat
hareketlerine göre **öneri ve bildirim** sunan ama fiyatları **hiçbir zaman
otomatik değiştirmeyen** yarı-otonom bir sistem.

## Temel Kural (mimarinin merkezi)

```
Taban Fiyat = Maliyet × (1 + Minimum Kâr Oranı / 100)
```

Sistem bu fiyatın altında **hiçbir koşulda** bir fiyat önermez. Piyasa fiyatı
düşse bile "fiyatı düşür" önerisi verilmez — sadece marj korunur. Bu kural
`backend/app/pricing.py` içindeki `evaluate_price()` fonksiyonunda tek bir
yerde uygulanır ve `backend/tests/test_pricing.py` ile test edilir.

Fiyat değişikliği **sadece** kullanıcı "Önerilen Fiyatı Uygula" butonuna
bastığında gerçekleşir (`crud.apply_recommendation`). Sistemin hiçbir
otomatik görevi (`scheduler.py`, `/scan-all`) `current_price` alanına
dokunmaz — sadece `market_price` alanını günceller.

## Proje Yapısı

```
market-price-advisor/
├── backend/                     # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── main.py              # API endpoint'leri
│   │   ├── models.py             # Products tablosu (SQLAlchemy ORM)
│   │   ├── schemas.py            # Pydantic request/response şemaları
│   │   ├── pricing.py            # KRİTİK: taban fiyat + öneri mantığı (saf fonksiyonlar)
│   │   ├── crud.py               # DB işlemleri + orkestrasyon
│   │   ├── scraper.py            # Modüler piyasa fiyatı sağlayıcısı (mock, gerçek scraper ile değiştirilebilir)
│   │   ├── scheduler.py          # Günlük otomatik tarama (APScheduler)
│   │   └── database.py           # SQLite/PostgreSQL bağlantısı
│   ├── tests/
│   │   └── test_pricing.py       # Taban fiyat kuralının testleri
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/                    # React + Vite
    ├── src/
    │   ├── api.js                 # Backend API istemcisi
    │   ├── App.jsx                # Layout + sekme yönlendirme
    │   ├── components/
    │   │   ├── Sidebar.jsx
    │   │   ├── Topbar.jsx
    │   │   ├── PriceRibbon.jsx    # İmza görsel: Taban/Mevcut/Piyasa fiyat şeridi
    │   │   ├── ProductFormModal.jsx
    │   │   └── Toast.jsx
    │   ├── pages/
    │   │   ├── DashboardPage.jsx  # Ürün tablosu
    │   │   └── RecommendationsPage.jsx  # Aksiyon gerektiren öneriler
    │   └── styles/
    ├── package.json
    └── .env.example
```

## Kurulum ve Çalıştırma

### 1) Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

API çalışır durumda: `http://127.0.0.1:8000`
İnteraktif dokümantasyon (Swagger UI): `http://127.0.0.1:8000/docs`

Testleri çalıştırmak için:
```bash
pytest tests/ -v
```

### 2) Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Panel: `http://localhost:5173`

> Not: Backend'i farklı bir adreste çalıştırıyorsanız `frontend/.env` içindeki
> `VITE_API_URL` değerini güncelleyin.

## API Uç Noktaları (Endpoints)

| Metod | Yol | Açıklama |
|---|---|---|
| `POST` | `/products` | Yeni ürün ekler |
| `GET` | `/products` | Tüm ürünleri, taban/piyasa/öneri bilgileriyle listeler |
| `GET` | `/products/{id}` | Tek ürün detayı |
| `PUT` | `/products/{id}` | Ürün bilgilerini günceller |
| `DELETE` | `/products/{id}` | Ürünü siler |
| `POST` | `/products/{id}/scan` | Tek ürün için piyasa taraması tetikler |
| `POST` | `/scan-all` | Tüm ürünler için piyasa taraması tetikler |
| `GET` | `/recommendations` | Sadece aksiyon gereken ürünleri döner |
| `POST` | `/products/{id}/apply-recommendation` | Kullanıcı onayıyla fiyatı günceller (**tek değişiklik noktası**) |
| `POST` | `/products/{id}/dismiss-recommendation` | Öneriyi fiyatı değiştirmeden kapatır |

## Gerçek Web Scraper'a Geçiş

`backend/app/scraper.py` içinde `MarketPriceProvider` soyut sınıfını
implemente eden yeni bir sınıf yazıp `get_active_provider()` fonksiyonunda
`MARKET_PROVIDER` ortam değişkenine bağlayın. Dosyada hazır bir iskelet
(`TrendyolScraperProvider` örneği) yorum satırı olarak bulunuyor. API,
scheduler ve frontend'de **hiçbir değişiklik gerekmez**.

## Veritabanı: SQLite → PostgreSQL

Varsayılan olarak SQLite kullanılır. PostgreSQL'e geçmek için `.env`
dosyasındaki `DATABASE_URL` değerini değiştirmeniz yeterlidir:

```
DATABASE_URL=postgresql://kullanici:sifre@localhost:5432/market_advisor
```

`psycopg2-binary` paketini `requirements.txt`'e eklemeniz gerekecek:
```bash
pip install psycopg2-binary
```

## Otomatik Tarama Sıklığı

`backend/app/main.py` içindeki `start_scheduler(hour=3, minute=0)` çağrısı
günlük taramanın saatini belirler. Farklı bir periyot (örn. her 6 saatte
bir) için `scheduler.py` içindeki `CronTrigger`'ı `IntervalTrigger` ile
değiştirebilirsiniz.
