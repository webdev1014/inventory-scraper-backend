import json
from flask import Flask, send_from_directory
from .util import remove_output_file
from .scraper import Scraper

APP = Flask(__name__, static_folder='static', static_url_path='/static')


def get_app():
    scraper = Scraper()
    scraper.run()

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
    remove_output_file()
    scraper = Scraper()
    scraper.stop()
    scraper.run()

    return json.dumps({'success': True})

@APP.route('/get_status', methods=['POST'])
def get_status():
    scraper = Scraper()

    return json.dumps({
        'success': True,
        'data': scraper.get_status()
    })
