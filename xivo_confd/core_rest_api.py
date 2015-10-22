# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging
import os
import urllib

from flask import Flask
from flask import request
from flask_cors import CORS
from werkzeug.contrib.fixers import ProxyFix
from xivo import http_helpers

from xivo_confd.authentication.confd_auth import ConfdAuth
from xivo_confd.helpers.common import handle_error
from xivo_confd.helpers.mooltiparse import parser as mooltiparse_parser
from xivo_confd.helpers.restful import ConfdApi
from xivo_confd import plugin_manager


from xivo_provd_client import new_provisioning_client_from_config


logger = logging.getLogger(__name__)


class CoreRestApi(object):

    def __init__(self, config):
        self.config = config
        self.content_parser = mooltiparse_parser()

        self.app = Flask('xivo_confd')
        http_helpers.add_logger(self.app, logger)
        self.app.wsgi_app = ProxyFix(self.app.wsgi_app)
        self.app.secret_key = os.urandom(24)
        self.app.config['auth'] = config['auth']
        self.auth = ConfdAuth()

        self.api = ConfdApi(self.app, prefix='/1.1')

        self.load_cors()

        if config['debug']:
            logger.info("Debug mode enabled.")
            self.app.debug = True

        plugin_manager.load_plugins(self)

        @self.app.before_request
        def log_requests():
            url = request.url.encode('utf8')
            url = urllib.unquote(url)
            params = {
                'method': request.method,
                'url': url,
            }
            if request.data:
                params.update({'data': request.data})
                logger.info("%(method)s %(url)s with data %(data)s ", params)
            else:
                logger.info("%(method)s %(url)s", params)

        @self.app.after_request
        def after_request(response):
            return http_helpers.log_request(response)

        @self.app.errorhandler(Exception)
        def error_handler(error):
            return handle_error(error)

    def load_cors(self):
        cors_config = dict(self.config['rest_api'].get('cors', {}))
        enabled = cors_config.pop('enabled', False)
        if enabled:
            CORS(self.app, **cors_config)

    def blueprint(self, name):
        return self.app.blueprints[name]

    def register(self, blueprint):
        self.app.register_blueprint(blueprint)

    def provd_client(self):
        return new_provisioning_client_from_config(self.config['provd'])

    def run(self):
        bind_addr = (self.config['rest_api']['listen'], self.config['rest_api']['port'])

        from cherrypy import wsgiserver
        wsgi_app = wsgiserver.WSGIPathInfoDispatcher({'/': self.app})
        server = wsgiserver.CherryPyWSGIServer(bind_addr=bind_addr,
                                               wsgi_app=wsgi_app)

        logger.debug('WSGIServer starting... uid: %s, listen: %s:%s', os.getuid(), bind_addr[0], bind_addr[1])

        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()
