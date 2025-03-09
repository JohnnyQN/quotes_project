from apscheduler.schedulers.background import BackgroundScheduler
from src.services import get_quote_of_the_day 
import logging

logger = logging.getLogger(__name__)

# Scheduler to update the quote of the day at midnight
def fetch_new_quote():
    logger.info("Running scheduled task to fetch a new quote of the day.")
    get_quote_of_the_day()

# Setting up the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_new_quote, trigger="cron", hour=0, minute=0)

if not scheduler.running:
    scheduler.start()
    logger.info("Background scheduler started.")
