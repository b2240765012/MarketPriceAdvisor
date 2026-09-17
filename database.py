"""
Veritabani baglanti ayarlari.

Varsayilan olarak SQLite kullanir (dosya: market_advisor.db).
PostgreSQL'e gecmek icin DATABASE_URL ortam degiskenini asagidaki gibi ayarlamaniz yeterli:

    DATABASE_URL=postgresql://kullanici:sifre@localhost:5432/market_advisor

SQLAlchemy iki motor arasinda soyutlama sagladigi icin kod tarafinda
baska hicbir degisiklik yapmaniza gerek yoktur.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./market_advisor.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: her istek icin bir DB oturumu acar ve sonda kapatir."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
