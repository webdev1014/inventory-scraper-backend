"""application.py -- top-level web application for inventory_source_scraper.
"""
from .web import get_app
# Init Flask app
APP = get_app()
