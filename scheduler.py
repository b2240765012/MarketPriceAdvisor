"""
Periyodik piyasa tarama zamanlayicisi.

APScheduler kullanarak gunde 1 kez (varsayilan: her gun 03:00) tum urunler
icin otomatik piyasa taramasi calistirir. Tarama SADECE market_price alanini
gunceller; current_price'a (satici fiyatina) hicbir zaman otomatik dokunmaz.
"""
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .database import SessionLocal
from . import crud

logger = logging.getLogger("scheduler")

scheduler = BackgroundScheduler()


def scan_all_products_job():
    db = SessionLocal()
    try:
        result = crud.scan_all_products(db)
        logger.info(
            "Otomatik piyasa taramasi tamamlandi: %s urun tarandi, %s tanesi aksiyon bekliyor.",
            result.scanned_count,
            result.action_needed_count,
        )
    finally:
        db.close()


def start_scheduler(hour: int = 3, minute: int = 0):
    """Uygulama baslarken cagrilir. Varsayilan: her gun saat 03:00."""
    if not scheduler.running:
        scheduler.add_job(
            scan_all_products_job,
            trigger=CronTrigger(hour=hour, minute=minute),
            id="daily_market_scan",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("Zamanlayici baslatildi: gunluk piyasa taramasi saat %02d:%02d", hour, minute)


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
