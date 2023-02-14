#!/usr/bin/env python3
# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging
import sys

from flask import Flask, jsonify, make_response, request

_EMPTY_RESPONSES = {'sounds': {}}

app = Flask(__name__)
websocket = None

_requests = []
_responses = {}

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def _reset():
    global _requests
    global _responses
    _requests = []
    _responses = dict(_EMPTY_RESPONSES)


@app.before_request
def log_request():
    if not request.path.startswith('/_'):
        path = request.path
        log = {
            'method': request.method,
            'path': path,
            'query': dict(request.args.items(multi=True)),
            'body': request.data.decode('utf-8'),
            'json': request.json if request.is_json else None,
            'headers': dict(request.headers),
        }
        _requests.append(log)


@app.route('/_requests', methods=['GET'])
def list_requests():
    return jsonify({'requests': _requests})


@app.route('/_reset', methods=['POST'])
def reset():
    _reset()
    return '', 204


@app.route('/_set_response', methods=['POST'])
def set_response():
    global _responses
    request_body = json.loads(request.data)
    set_response = request_body['response']
    set_response_body = request_body['content']
    _responses[set_response] = set_response_body
    return '', 204


@app.route('/ari/sounds', methods=['GET'])
def get_sounds():
    return make_response(
        json.dumps(_responses.get('sounds', [])),
        200,
        {'Content-Type': 'application/json'},
    )


@app.route('/ari/sounds/<sound_id>', methods=['GET'])
def get_sound(sound_id):
    sound = _responses.get(f'sounds/{sound_id}')
    if not sound:
        return '', 404
    return jsonify(sound)


_reset()


if __name__ == '__main__':
    port = int(sys.argv[1])
    app.run(host='0.0.0.0', port=port, debug=True)
