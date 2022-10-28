# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import signal

from functools import partial

import xivo_dao

from wazo_auth_client import Client as AuthClient
from xivo import plugin_helpers
from xivo.consul_helpers import ServiceCatalogRegistration
from xivo.status import StatusAggregator, TokenStatus
from xivo.token_renewer import TokenRenewer

from wazo_confd.helpers.asterisk import PJSIPDoc

from . import auth
from ._bus import BusPublisher, BusConsumer
from .http_server import api, app, HTTPServer
from .service_discovery import self_check

logger = logging.getLogger(__name__)


class ServiceHandle:

    def __init__(self):
        self._services = {}

    def register(self, service_name, service):
        self._services[service_name] = service

    def get(self, service_name):
        return self._services[service_name]


class Controller:
    def __init__(self, config):
        self.config = config
        self._bus_consumer = BusConsumer.from_config(config['bus'])
        self._bus_publisher = BusPublisher.from_config(config['uuid'], config['bus'])
        self._bus_publisher.set_as_reference()
        self.status_aggregator = StatusAggregator()
        self.token_status = TokenStatus()
        self._service_discovery_args = [
            'wazo-confd',
            config['uuid'],
            config['consul'],
            config['service_discovery'],
            config['bus'],
            partial(self_check, config),
        ]
        self.http_server = HTTPServer(config)
        auth_client = AuthClient(**config['auth'])
        self.token_renewer = TokenRenewer(auth_client)
        if not app.config['auth'].get('master_tenant_uuid'):
            self.token_renewer.subscribe_to_next_token_details_change(
                auth.init_master_tenant
            )
        pjsip_doc = PJSIPDoc(config['pjsip_config_doc_filename'])
        self.token_renewer.subscribe_to_token_change(
            self.token_status.token_change_callback
        )
        self.status_aggregator.add_provider(auth.provide_status)
        self.status_aggregator.add_provider(self.token_status.provide_status)
        self.status_aggregator.add_provider(self._bus_consumer.provide_status)

        service_handle = ServiceHandle()

        plugin_helpers.load(
            namespace='wazo_confd.plugins',
            names=config['enabled_plugins'],
            dependencies={
                'api': api,
                'config': config,
                'token_changed_subscribe': self.token_renewer.subscribe_to_token_change,
                'bus_consumer': self._bus_consumer,
                'bus_publisher': self._bus_publisher,
                'auth_client': auth_client,
                'pjsip_doc': pjsip_doc,
                'service_handle': service_handle,
                'status_aggregator': self.status_aggregator,
            },
        )

    def run(self):
        logger.info('wazo-confd starting...')
        xivo_dao.init_db_from_config(self.config)
        signal.signal(signal.SIGTERM, partial(_sigterm_handler, self))

        with self.token_renewer:
            with self._bus_consumer:
                with ServiceCatalogRegistration(*self._service_discovery_args):
                    self.http_server.run()

    def stop(self, reason):
        logger.warning('Stopping wazo-confd: %s', reason)
        self.http_server.stop()


def _sigterm_handler(controller, signum, frame):
    controller.stop(reason='SIGTERM')
