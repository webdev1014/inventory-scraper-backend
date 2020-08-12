#!/usr/bin/env bash
celery -A inventory_source_scraper.application.celery worker --logfile="logs/error.log" -l ERROR --concurrency=8
