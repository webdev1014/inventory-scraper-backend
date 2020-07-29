import json
from flask import Flask, send_from_directory, jsonify, url_for
from celery.result import AsyncResult
from .util import remove_output_file
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
    remove_output_file()
    task = APP.celery.tasks[Scraper.name].apply_async()
    return jsonify({'task_id': task.id})


@APP.route('/get_status/<task_id>', methods=['POST'])
def get_status(task_id):
    task = AsyncResult(task_id, app=APP.celery)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'PENDING'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': 'FAILURE'
        }

    print(jsonify(response))
    return jsonify(response)
