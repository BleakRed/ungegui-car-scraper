import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def start_scheduler():
    from .scraper import run_scraper

    interval_hours = int(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))

    def job():
        logger.info("Scheduler: starting scheduled scrape")
        try:
            run_scraper(max_pages=5)
        except Exception as e:
            logger.error(f"Scheduled scrape failed: {e}")

    scheduler.add_job(
        job,
        trigger=IntervalTrigger(hours=interval_hours),
        id="scrape_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started: scraping every {interval_hours} hours")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
