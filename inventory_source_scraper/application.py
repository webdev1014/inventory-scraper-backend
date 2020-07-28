"""application.py -- top-level web application for inventory_source_scraper.
"""
from celery import Celery
from .scraper import Scraper
from .web import get_app

# Init Flask app
APP = get_app()

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
celery = Celery(APP.name, backend=CELERY_RESULT_BACKEND, broker=CELERY_BROKER_URL)
celery.register_task(Scraper())

APP.celery = celery
