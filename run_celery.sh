#!/usr/bin/env bash
celery -A inventory_source_scraper.application.celery worker -l warn
