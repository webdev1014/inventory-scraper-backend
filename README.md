# Inventory Source Scraper

### Run redis server
. run_redis.sh

### Start a Celery worker:
celery -A inventory_source_scraper.application.celery worker -l warn 