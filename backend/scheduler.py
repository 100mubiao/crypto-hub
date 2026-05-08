import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.config import settings
from backend.crawler import crawl_market_data, crawl_trending, seed_alerts, seed_initial_data

logger = logging.getLogger("scheduler")


async def run_crawl_job():
    logger.info("Scheduled crawl job starting...")
    try:
        await crawl_market_data()
    except Exception as e:
        logger.error("Market crawl failed: %s", e)
    try:
        await crawl_trending()
    except Exception as e:
        logger.error("Trending crawl failed: %s", e)
    logger.info("Scheduled crawl job finished.")


def start_scheduler():
    seed_initial_data()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_crawl_job,
        "interval",
        minutes=settings.crawler_interval_minutes,
        id="crawl_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started (interval=%d min)", settings.crawler_interval_minutes)
