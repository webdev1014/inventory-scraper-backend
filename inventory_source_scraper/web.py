import json
from flask import Flask, send_from_directory, jsonify, url_for
from .database import Database
from .scraper import Scraper

APP = Flask(__name__, static_folder='static', static_url_path='/static')


def get_app():
    APP.config.from_mapping(
        SECRET_KEY='inventory_source_scraper'
    )
    APP.config.update(CELERYD_HIJACK_ROOT_LOGGER=False)
    return APP


# Flask default route to catch all unhandled URLs
# https://stackoverflow.com/questions/13678397/python-flask-default-route-possible
@APP.route('/', defaults={'path': ''})
@APP.route('/<path:path>')
def index(path=None):
    return json.dumps({'success': True})


@APP.route('/get_output', methods=['GET', 'POST'])
def get_output():

    return send_from_directory(APP.static_folder, 'output.xlsx', as_attachment=True)


@APP.route('/start', methods=['POST'])
def restart():
    db = Database()
    status = db.get_status()

    if status != 'RUNNING':
        APP.celery.tasks[Scraper.name].apply_async()
    return jsonify({'success': True, 'status': status})


@APP.route('/get_status', methods=['POST'])
def get_status():
    db = Database()
    status = db.get_status()

    return jsonify({'success': True, 'status': status})
